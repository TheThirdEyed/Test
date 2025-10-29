import { render } from 'solid-js/web';

function App() {
  return (
    <main style={{padding:'2rem',fontFamily:'sans-serif'}}>
      <h1>Multi-Agent Docs Frontend</h1>
      <p>Frontend connected via Nginx proxy to backend.</p>
    </main>
  );
}

render(() => <App />, document.getElementById('root'));
