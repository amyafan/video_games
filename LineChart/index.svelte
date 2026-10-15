<script>
	import { extent, groups, max, range } from 'd3-array';
	import { format } from 'd3-format';
	import { scaleLinear, scaleTime } from 'd3-scale';
	import { line } from 'd3-shape';

	import { prefersDarkInApp } from '$lib/shared/stores.js';

	import AxisBottom from './_components/Axis/AxisBottom.svelte';
	import AxisLeft from './_components/Axis/AxisLeft.svelte';

	import dodge from './_utils/dodge';

	// Import data and coerce types
	import data from './_data/nb_5_final.xlsx - for_graphic.csv';
	data.forEach((d) => {
		d.Hours = +d.Hours;
		return d;
	});

	const grouped = groups(data, (d) => d.Activity);

	// Dimensions
	let w;
	const margin = { left: 18, right: 18, top: 6, bottom:20};
	$: width = w - margin.left - margin.right;
	$: height = Math.max(width * 0.5, 300);

	// Scales
	$: x = scaleLinear(
		extent(data, (d) => d.Year),
		[0, width]
	);
	$: y = scaleLinear([0, max(data, (d) => d.Hours)], [height, 0]);

	// Generator
	$: lineGenerator = line(
		(d) => x(d.Year),
		(d) => y(d.Hours)
	);

	// Label dodging
	let dodged;
	$: if (width) {
		dodged = dodge(
			grouped.map(([, entries]) => y(entries[10].Hours)),
			50
		);
	}

	$: tickLineMajor = $prefersDarkInApp ? '#ededed' : '#7a7a7a';
	$: tickLineMinor = $prefersDarkInApp ? '#a8a8a8' : '#dedede';
	$: tickText = $prefersDarkInApp ? '#ededed' : '#7a7a7a';

</script>

<div class="g-chart-line" bind:clientWidth={w}>
	<svg width={width + margin.left + margin.right} height={height + margin.top + margin.bottom}>
		<g transform="translate({margin.left}, {margin.top})">
			<AxisBottom
				scale={x}
				tickLineStroke={tickLineMajor}
				tickPadding={-1}
				tickSize={5}
				tickTextAnchor="start"
				tickTextDx={-17}
				tickTextDy={15}
				tickTextFill={tickText}
				translate={[0, height]}
			/>

			<AxisLeft
				scale={y}
				tickLineStroke={(_, i) => (i === 0 ? tickLineMajor : tickLineMinor)}
				tickPadding={0}
				tickSize={width + margin.left}
				tickTextAnchor="start"
				tickTextDy={-3}
				tickTextFill={(d) => (d === 0 ? 'transparent' : tickText)}
				tickValues={range(0, 20, 5)}
				translate={[width]}
			/>

			{#each grouped as [Activity, Hours], i (Activity)}
				<g class="g-line g-line-{Activity.slice(-2).toLowerCase()}">
					<path d={lineGenerator(Hours)} />
					{#if dodged}
						{#if Activity === "Playing sports"}
							<text dx="-70" dy="0" x={width} y={dodged[i]}>
								<tspan>Playing sports</tspan>
							</text>
						{:else if Activity === "Watching TV"}
							<text dx="0" dy="70" x={0.05*(width-35)+ 10} y={-50}>
								<tspan>Watching TV</tspan>
							</text>
						
						{:else if Activity === "Playing games"}
							<text dx=-65 dy="-30" x={0.75*(width-50)+18} y={dodged[i]} font-weight = "bold">{Activity}
							</text>
						
						{:else if Activity === "Socializing"}
							<text dx="-50" dy="0" x={width} y={dodged[i]}>{Activity}	
							</text>						
						{/if}
					{/if}
					{console.log({Activity})}
				</g>
			{/each}
		</g>
	</svg>
</div>

<style>
	:global(.g-chart-line) {
		--g-label-fill: #333;
		--g-tv-stroke: #C1CBE3;
		--g-es-stroke: #404D6E;
		--g-ts-stroke: #E8EDFC;
		--g-ng-stroke: #D5DDF0;
	}

	@media (prefers-color-scheme: dark) {
		:global(html.NYTApp .g-dark-mode-compatible .g-chart-line) {
			--g-label-fill: #f5f5f5;
			--g-tv-stroke: #636363;
			--g-es-stroke: #ffffff;
			--g-ts-stroke: #7A7A7A;
			--g-ng-stroke: #919191;
		}
	}

	.g-line path {
		fill: none;
		stroke-linejoin: round;
		stroke-width: 2px;
		stroke: orange;
	}
	.g-line-tv path {
		stroke: var(--g-tv-stroke);
	}
	.g-line-es path {
		stroke: var(--g-es-stroke);
	}
	.g-line-ts path {
		stroke: var(--g-ts-stroke);
	}
	.g-line-ng path {
		stroke: var(--g-ng-stroke);
	}

	.g-line text {
		fill: var(--g-label-fill);
		font-family: var(--g-franklin);
		white-space: pre;
		font-size:10pt;
	}

	.text{
		
	}
</style>
