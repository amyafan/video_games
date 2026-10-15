"""
AF 7-2025

cleaning all the files


    inputs:
    ______

        zip files

    outputs:
    _______

        parquets

the bigger files (atuscps, atusact) don't fit in memory as a pandas dataframe,
so each .dat is streamed into its parquet one block at a time.

"""

import re
from pathlib import Path
from zipfile import ZipFile

import pyarrow as pa
import pyarrow.csv as pv
import pyarrow.parquet as pq


DATA = Path(__file__).resolve().parent.parent / "data"
SOURCE = DATA / "source"
PROCESSED = DATA / "processed"

YEAR = "0324"

# keep the times as "HH:MM:SS" strings, like the old CSVs -- otherwise arrow turns them into time objects
FORCE_TYPES = {"TUSTARTTIM": pa.string(), "TUSTOPTIME": pa.string()}

# if a column turns out not to fit its type, widen it: int64 -> float64 -> string
WIDER = {pa.int64(): pa.float64(), pa.float64(): pa.string()}


def get_files(source, year):
    return sorted((source / year).glob(f"atus*-{year}.zip"))


def dat_to_parquet(zip_path, out_path, block_size=64 << 20):
    """stream the .dat inside a BLS zip into a parquet file, one block at a time

    arrow guesses each column's type from the first block. if a later block has a value
    that doesn't fit (e.g. a 4.5 in a column that looked like integers), arrow errors,
    so we widen that column's type and start over.

    lower block_size if memory is still tight.
    """

    column_types = dict(FORCE_TYPES)
    tmp_path = out_path.with_suffix(".parquet.tmp")

    while True:
        try:
            with ZipFile(zip_path) as z:
                dat_name = next(n for n in z.namelist() if n.endswith(".dat"))
                with z.open(dat_name) as f:
                    reader = pv.open_csv(f, read_options=pv.ReadOptions(block_size=block_size),
                                         convert_options=pv.ConvertOptions(column_types=column_types))
                    schema = reader.schema
                    with pq.ParquetWriter(tmp_path, schema) as writer:
                        for batch in reader:
                            writer.write_batch(batch)
            break

        except pa.ArrowInvalid as e:
            match = re.search(r"CSV column #(\d+)", str(e))
            if not match:
                raise
            col = schema.field(int(match.group(1)))
            if col.type not in WIDER:
                raise
            column_types[col.name] = WIDER[col.type]
            print(f"  {col.name}: {col.type} -> {column_types[col.name]}, restarting")

    # only replace the real file once the whole thing has been written
    tmp_path.replace(out_path)


def main(source, processed, year):
    zip_files = get_files(source, year)

    (processed / year).mkdir(parents=True, exist_ok=True)

    for atuspath in zip_files:
        print(atuspath)

        outfile_name = processed / year / (atuspath.stem + ".parquet")
        dat_to_parquet(atuspath, outfile_name)

        print(f"finished writing {outfile_name}")



if __name__ == "__main__":

    main(SOURCE, PROCESSED, YEAR)
