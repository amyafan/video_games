export default function valueOrFunction(prop, d, i, e) {
	return !prop ? null : typeof prop === 'function' ? prop(d, i, e) : prop;
}
