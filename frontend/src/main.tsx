
import { render } from "solid-js/web";
import { createSignal, onCleanup, Show, For } from "solid-js";
import Diagram from "./Diagram";
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const WS_BASE = import.meta.env.VITE_WS_BASE || "ws://localhost:8000";
type Project = { id:number; name:string; status:string; personas:string; repo_source:string; repo_url?:string };
function App(){
  const [email,setEmail]=createSignal(""); const [password,setPassword]=createSignal(""); const [token,setToken]=createSignal<string|null>(null);
  const [projects,setProjects]=createSignal<Project[]>([]); const [selected,setSelected]=createSignal<number|null>(null); const [log,setLog]=createSignal<string[]>([]);
  const [artifacts,setArtifacts]=createSignal<any[]>([]); let ws:WebSocket|null=null;
  const [projectName,setProjectName]=createSignal("Demo Project"); const [personas,setPersonas]=createSignal<"SDE"|"PM"|"SDE,PM">("SDE,PM");
  const [repoUrl,setRepoUrl]=createSignal(""); const [zipFile,setZipFile]=createSignal<File|null>(null);
  const [depth,setDepth]=createSignal<"quick"|"standard"|"deep">("standard"); const [verbosity,setVerbosity]=createSignal<"low"|"standard"|"high">("standard");

  async function signup(){ const r=await fetch(`${API_BASE}/auth/signup`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:email(),password:password(),role:"User"})}); const d=await r.json(); if(d.access_token) setToken(d.access_token); }
  async function login(){ const r=await fetch(`${API_BASE}/auth/login`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:email(),password:password()})}); const d=await r.json(); if(d.access_token) setToken(d.access_token); }
  function invalidateZipIfRepoUrl(v:string){ setRepoUrl(v); if(v.trim()) setZipFile(null); }
  function invalidateRepoUrlIfZip(f:File|null){ setZipFile(f); if(f) setRepoUrl(""); }
  async function createProject(){
    if(!projectName().trim()) return alert("Project name required");
    if(!repoUrl().trim() && !zipFile()) return alert("Provide either a repo URL or a ZIP");
    const form=new FormData(); form.append("name",projectName()); form.append("personas",personas()); if(repoUrl().trim()) form.append("repo_url",repoUrl()); if(zipFile()) form.append("file",zipFile() as File);
    const res=await fetch(`${API_BASE}/projects`,{method:"POST",body:form}); const p=await res.json(); setProjects([p,...projects()]); }
  async function startAgents(p:Project){
    const res=await fetch(`${API_BASE}/agents/start`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({project_id:p.id,depth:depth(),verbosity:verbosity(),personas:personas()})}); await res.json(); connectWS(p.id);
  }
  function connectWS(id:number){ setSelected(id); ws?.close(); ws=new WebSocket(`${WS_BASE}/analysis/ws/${id}`); ws.onmessage=(ev)=>{ const d=JSON.parse(ev.data); if(d.message) setLog((prev)=>[`${d.message}`,...prev].slice(0,200)); }; }
  async function pause(){ if(selected()==null) return; await fetch(`${API_BASE}/agents/pause/${selected()}`,{method:"POST"}); }
  async function resume(){ if(selected()==null) return; await fetch(`${API_BASE}/agents/resume/${selected()}`,{method:"POST"}); }
  async function refreshArtifacts(){ if(selected()==null) return; const res=await fetch(`${API_BASE}/agents/artifacts/${selected()}`); setArtifacts(await res.json()); }
  onCleanup(()=>ws?.close());

  return (<div style={{"font-family":"ui-sans-serif, system-ui",padding:"1.25rem","max-width":"1000px",margin:"0 auto"}}>
    <h1>Multi‑Agent Code Docs — LLM Build</h1>
    <section style={{display:"grid","grid-template-columns":"1fr 1fr",gap:"1rem","align-items":"end"}}>
      <div><label>Email</label><input value={email()} onInput={(e)=>setEmail(e.currentTarget.value)} style={{width:"100%",padding:".5rem"}}/></div>
      <div><label>Password</label><input type="password" value={password()} onInput={(e)=>setPassword(e.currentTarget.value)} style={{width:"100%",padding:".5rem"}}/></div>
      <button onClick={signup} style={{padding:".6rem 1rem"}}>Sign up</button><button onClick={login} style={{padding:".6rem 1rem"}}>Log in</button>
    </section>
    <Show when={token()}>
      <hr/>
      <h3>Create Project</h3>
      <section style={{display:"grid","grid-template-columns":"1fr 1fr",gap:".75rem"}}>
        <input placeholder="Project name" value={projectName()} onInput={(e)=>setProjectName(e.currentTarget.value)}/>
        <select value={personas()} onInput={(e)=>setPersonas(e.currentTarget.value as any)}>
          <option value="SDE,PM">Both (SDE & PM)</option><option value="SDE">SDE only</option><option value="PM">PM only</option>
        </select>
        <input placeholder="Git repository URL (https://github.com/org/repo.git)" value={repoUrl()} onInput={(e)=>invalidateZipIfRepoUrl(e.currentTarget.value)}/>
        <input type="file" onChange={(e)=>invalidateRepoUrlIfZip(e.currentTarget.files?.[0]||null)}/>
        <div><label>Depth:</label><select value={depth()} onInput={(e)=>setDepth(e.currentTarget.value as any)}><option value="quick">Quick</option><option value="standard">Standard</option><option value="deep">Deep</option></select></div>
        <div><label>Verbosity:</label><select value={verbosity()} onInput={(e)=>setVerbosity(e.currentTarget.value as any)}><option value="low">Low</option><option value="standard">Standard</option><option value="high">High</option></select></div>
        <button onClick={createProject} style={{padding:".6rem 1rem"}}>Create</button>
      </section>
      <h3>Projects</h3>
      <ul><For each={projects()}>{(p)=>(
        <li style={{display:"flex","justify-content":"space-between","align-items":"center",padding:".5rem 0"}}>
          <span>#{p.id} — {p.name} — {p.status} {p.repo_url?`— ${p.repo_url}`:""}</span>
          <div style={{display:"flex",gap:".5rem"}}>
            <button onClick={()=>startAgents(p)}>Start Agents</button>
            <button onClick={()=>connectWS(p.id)}>Connect</button>
            <button onClick={pause}>Pause</button><button onClick={resume}>Resume</button>
            <button onClick={refreshArtifacts}>Artifacts</button>
          </div>
        </li>)}</For></ul>
      <h3>Activity</h3>
      <div style={{"min-height":"160px",border:"1px solid #ddd",padding:".75rem"}}><For each={log()}>{(line)=><div>{line}</div>}</For></div>
      <Show when={artifacts().length}>
        <h3>Artifacts</h3>
        <ul><For each={artifacts()}>{(a)=><Artifact id={a.id} title={a.title}/>}</For></ul>
      </Show>
    </Show>
  </div>);
}
function Artifact(props:{id:number; title:string}){
  const [md,setMd]=createSignal(""); async function load(){ const res=await fetch(`${API_BASE}/agents/artifact/${props.id}`); const data=await res.json(); setMd(data.content_md||""); }
  return (<li style={{margin:".25rem 0"}}>
    <button onClick={load}>{props.title}</button>
    <Show when={md()}>
      <div style={{padding:".5rem",border:"1px solid #eee","margin-top":".25rem"}}><MermaidBlock markdown={md()}/></div>
    </Show>
  </li>);
}
function MermaidBlock(props:{markdown:string}){
  const code=extractMermaid(props.markdown)||"graph TD; A-->B;"; return <Diagram code={code}/>;
}
function extractMermaid(md:string):string|null{
  const fence="```mermaid"; const start=md.indexOf(fence); if(start===-1) return null; const end=md.indexOf("```", start+fence.length); if(end===-1) return null; return md.substring(start+fence.length,end).trim();
}
render(()=> <App/>, document.getElementById("root") as HTMLElement);
