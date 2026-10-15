<script>
	import Axis from './index.svelte';

	export let scale;

	export let domain = false;
	export let domainStroke = '#a8a8a8';
	export let domainStrokeDasharray = 'none';
	export let domainStrokeWidth = 1;
	export let domainTranslate = [0, 0];

	export let tickFormat = (d) => d;
	export let tickLineStroke = '#a8a8a8';
	export let tickLineStrokeDasharray = 'none';
	export let tickLineStrokeWidth = 1;
	export let tickTextAnchor = 'middle';
	export let tickTextDx = 0;
	export let tickTextDy = '0em';
	export let tickTextFill = '#7a7a7a';
	export let tickTextFontSize = '14px';
	export let tickTextFontWeight = 400;
	export let tickSize = 6;
	export let tickPadding = 3;
	export let tickValues = [];

	export let translate = [0, 0];
</script>

<Axis
	orientation="top"
	{scale}
	{domain}
	{domainStroke}
	{domainStrokeDasharray}
	{domainStrokeWidth}
	{domainTranslate}
	{tickFormat}
	{tickLineStroke}
	{tickLineStrokeDasharray}
	{tickLineStrokeWidth}
	{tickPadding}
	{tickSize}
	{tickTextAnchor}
	{tickTextDx}
	{tickTextDy}
	{tickTextFill}
	{tickTextFontSize}
	{tickTextFontWeight}
	{tickValues}
	{translate}
/>
