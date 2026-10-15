// Non-exhaustive helper that returns a string label.
// Extend or tweak as needed.
export default function scaleType(scale) {
	if (typeof scale.bandwidth === 'function') {
		// Band and point scales both expose .bandwidth().
		// Point scales return 0 for bandwidth(), so you can split them if needed.
		return scale.bandwidth() === 0 ? 'point' : 'band';
	}

	if (typeof scale.quantiles === 'function') return 'quantile'; // quantile() only
	if (typeof scale.thresholds === 'function') return 'quantize'; // quantize() only
	if (typeof scale.invertExtent === 'function') return 'threshold'; // threshold() only

	// Continuous scales share .invert().
	if (typeof scale.invert === 'function') {
		// Sequential scales lack .ticks(), so look for it:
		return typeof scale.ticks === 'function' ? 'continuous' : 'sequential';
	}

	// If none of the above match we fall back to ordinal (the most generic).
	return 'ordinal';
}
