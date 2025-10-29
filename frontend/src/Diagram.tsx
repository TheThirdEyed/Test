
import mermaid from "mermaid";
import { onMount, createSignal } from "solid-js";
export default function Diagram(props: { code: string }) {
  const [html, setHtml] = createSignal("");
  onMount(async () => {
    mermaid.initialize({ startOnLoad: false });
    try { const { svg } = await mermaid.render(`m-${Date.now()}`, props.code); setHtml(svg); }
    catch (e) { setHtml(`<pre>${props.code}</pre>`); }
  });
  return <div innerHTML={html()} />;
}
