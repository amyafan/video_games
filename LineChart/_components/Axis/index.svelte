<script>
	import scaleType from './scaleType';
	import valueOrFunction from './valueOrFunction';

	// can be "bottom", "left", "top", "right"
	export let orientation = 'bottom';

	// a d3-scale
	export let scale;

	export let domain = false;
	export let domainStroke = '#a8a8a8';
	export let domainStrokeDasharray = 'none';
	export let domainStrokeWidth = 1;
	export let domainTranslate = [0, 0];

	export let tickValues = [];
	export let tickFormat = (d) => d;
	export let tickLineStroke = '#a8a8a8';
	export let tickLineStrokeDasharray = 'none';
	export let tickLineStrokeWidth = 1;
	export let tickTextAnchor = 'middle';
	export let tickTextDx = 0;
	export let tickTextDy = '0.71em';
	export let tickTextFill = '#7a7a7a';
	export let tickTextFontSize = '14px';
	export let tickTextFontWeight = 400;
	export let tickSize = 6;
	export let tickPadding = 3;

	export let translate = [0, 0];

	const type = scaleType(scale);

	let ticks;
	if (tickValues.length) {
		ticks = tickValues;
	} else if (type === 'band') {
		ticks = scale?.domain() || [];
	} else {
		ticks = scale?.ticks() || [];
	}

	let years = [2004, 2009, 2014, 2019, 2024]

	if(ticks[0]>1000) {
		ticks = years;
	}
		const tickTranslate = (tick) => scale(tick) + (type === 'band' ? scale.bandwidth() / 2 : 0);
</script>

<g class="g-axis" transform={`translate(${translate})`}>
	{#each ticks as tick, tickIndex (tickIndex)}
		<g
			class="g-tick"
			transform="translate({['bottom', 'top'].includes(orientation)
				? [tickTranslate(tick), 0]
				: [0, tickTranslate(tick)]})"
		>
			<line
				{...{
					stroke: valueOrFunction(tickLineStroke, tick, tickIndex, ticks),
					'stroke-dasharray': valueOrFunction(tickLineStrokeDasharray, tick, tickIndex, ticks),
					'stroke-width': valueOrFunction(tickLineStrokeWidth, tick, tickIndex, ticks),
					/* orientation‑specific part */
					[['bottom', 'top'].includes(orientation) ? 'y2' : 'x2']:
						valueOrFunction(tickSize, tick, tickIndex, ticks) *
						(['bottom', 'right'].includes(orientation) ? 1 : -1)
				}}
			/>

			<text
				{...{
					dx: valueOrFunction(tickTextDx, tick, tickIndex, ticks),
					dy: valueOrFunction(tickTextDy, tick, tickIndex, ticks),
					fill: valueOrFunction(tickTextFill, tick, tickIndex, ticks),
					'font-size': valueOrFunction(tickTextFontSize, tick, tickIndex, ticks),
					'font-weight': valueOrFunction(tickTextFontWeight, tick, tickIndex, ticks),
					'text-anchor': valueOrFunction(tickTextAnchor, tick, tickIndex, ticks),
					[['bottom', 'top'].includes(orientation) ? 'y' : 'x']:
						(valueOrFunction(tickSize, tick, tickIndex, ticks) +
							valueOrFunction(tickPadding, tick, tickIndex, ticks)) *
						(['bottom', 'right'].includes(orientation) ? 1 : -1)
				}}
			>
				{@html tickFormat(tick, tickIndex, ticks)}
			</text>
		</g>
	{/each}
	{#if domain}
		<line
			{...{
				stroke: domainStroke,
				'stroke-dasharray': domainStrokeDasharray,
				'stroke-width': domainStrokeWidth,
				[['bottom', 'top'].includes(orientation) ? 'x2' : 'y2']: Math.abs(
					scale.range()[scale.range().length - 1] - scale.range()[0]
				),
				transform: `translate(${domainTranslate})`
			}}
		/>
	{/if}
</g>

<style>
	.g-axis .g-tick text {
		font-family: var(--g-franklin);
	}
</style>
