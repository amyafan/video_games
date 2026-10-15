import { ascending, range } from 'd3-array';

// Takes an array of numbers representing the y-coordinate
// See https://observablehq.com/@d3/slope-chart/3
export default function dodge(positions, separation = 10, maxiter = 10, maxerror = 1e-1) {
	let n = positions.length;
	if (!positions.every(isFinite)) throw new Error('invalid position');
	if (!(n > 1)) return positions;
	let index = range(positions.length);
	for (let iter = 0; iter < maxiter; ++iter) {
		index.sort((i, j) => ascending(positions[i], positions[j]));
		let error = 0;
		for (let i = 1; i < n; ++i) {
			let delta = positions[index[i]] - positions[index[i - 1]];
			if (delta < separation) {
				delta = (separation - delta) / 2;
				error = Math.max(error, delta);
				positions[index[i - 1]] -= delta;
				positions[index[i]] += delta;
			}
		}
		if (error < maxerror) break;
	}
	return positions;
}
