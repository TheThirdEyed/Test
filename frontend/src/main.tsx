
import { render } from "solid-js/web";
import { createSignal, onCleanup, Show, For } from "solid-js";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const WS_BASE = import.meta.env.VITE_WS_BASE || "ws://localhost:8000";

function App() {
  const [email, setEmail] = createSignal("");
  const [password, setPassword] = createSignal("");
  const [token, setToken] = createSignal<string | null>(null);
  const [projects, setProjects] = createSignal<any[]>([]);
  const [selected, setSelected] = createSignal<number | null>(null);
  const [log, setLog] = createSignal<string[]>([]);
  let ws: WebSocket | null = null;

  async function signup() {
    const res = await fetch(`${API_BASE}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email(), password: password(), role: "User" }),
    });
    const data = await res.json();
    if (data.access_token) setToken(data.access_token);
  }

  async function login() {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email(), password: password() }),
    });
    const data = await res.json();
    if (data.access_token) setToken(data.access_token);
  }

  async function createProject() {
    const form = new FormData();
    form.append("name", "Demo Project");
    form.append("personas", "SDE,PM");
    const res = await fetch(`${API_BASE}/projects`, { method: "POST", body: form });
    const p = await res.json();
    setProjects([p, ...projects()]);
  }

  async function startAnalysis(id: number) {
    await fetch(`${API_BASE}/analysis/${id}/start`, { method: "POST" });
    connectWS(id);
  }

  function connectWS(id: number) {
    setSelected(id);
    ws?.close();
    ws = new WebSocket(`${WS_BASE}/analysis/ws/${id}`);
    ws.onmessage = (ev) => {
      const d = JSON.parse(ev.data);
      setLog((prev) => [`${d.stage}: ${d.progress}%`, ...prev].slice(0, 100));
    };
    ws.onclose = () => {};
  }

  async function pause() {
    if (selected() == null) return;
    await fetch(`${API_BASE}/analysis/${selected()}/pause`, { method: "POST" });
  }

  async function resume() {
    if (selected() == null) return;
    await fetch(`${API_BASE}/analysis/${selected()}/resume`, { method: "POST" });
  }

  onCleanup(() => ws?.close());

  return (
    <div style={{ "font-family": "ui-sans-serif, system-ui", padding: "1.25rem", "max-width": "900px", margin: "0 auto" }}>
      <h1>Multi‑Agent Code Docs — Demo</h1>

      <section style={{ display: "grid", "grid-template-columns": "1fr 1fr", gap: "1rem", "align-items": "end" }}>
        <div>
          <label>Email</label>
          <input value={email()} onInput={(e) => setEmail(e.currentTarget.value)} style={{ width: "100%", padding: ".5rem" }} />
        </div>
        <div>
          <label>Password</label>
          <input type="password" value={password()} onInput={(e) => setPassword(e.currentTarget.value)} style={{ width: "100%", padding: ".5rem" }} />
        </div>
        <button onClick={signup} style={{ padding: ".6rem 1rem" }}>Sign up</button>
        <button onClick={login} style={{ padding: ".6rem 1rem" }}>Log in</button>
      </section>

      <Show when={token()}>
        <hr />
        <section style={{ display: "flex", gap: ".5rem", "align-items": "center" }}>
          <button onClick={createProject} style={{ padding: ".6rem 1rem" }}>New Project</button>
          <button disabled={selected()==null} onClick={pause} style={{ padding: ".6rem 1rem" }}>Pause</button>
          <button disabled={selected()==null} onClick={resume} style={{ padding: ".6rem 1rem" }}>Resume</button>
        </section>

        <h3>Projects</h3>
        <ul>
          <For each={projects()}>
            {(p) => (
              <li style={{ display: "flex", "justify-content": "space-between", "align-items": "center", padding: ".5rem 0" }}>
                <span>#{p.id} — {p.name} — {p.status}</span>
                <div style={{ display: "flex", gap: ".5rem" }}>
                  <button onClick={() => startAnalysis(p.id)}>Start</button>
                  <button onClick={() => connectWS(p.id)}>Connect</button>
                </div>
              </li>
            )}
          </For>
        </ul>

        <h3>Activity</h3>
        <div style={{ "min-height": "160px", border: "1px solid #ddd", padding: ".75rem" }}>
          <For each={log()}>{(line) => <div>{line}</div>}</For>
        </div>
      </Show>
    </div>
  );
}

render(() => <App />, document.getElementById("root") as HTMLElement);
