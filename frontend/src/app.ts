const API = 'http://localhost:8000/api/v1';

interface Stack {
  id: number;
  name: string;
  compose_path: string;
}

interface TokenResponse {
  access_token: string;
}

let token = localStorage.getItem('sf_token') ?? '';

const authPanel = document.getElementById('auth-panel')!;
const stackList = document.getElementById('stack-list')!;
const logView = document.getElementById('log-view')!;
const stackForm = document.getElementById('stack-form') as HTMLFormElement;

function headers(): HeadersInit {
  return token ? { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };
}

function renderAuth(): void {
  authPanel.innerHTML = token
    ? '<span>logged in</span> <button id="logout">logout</button>'
    : `<input id="email" placeholder="email" />
       <input id="pass" type="password" placeholder="password" />
       <button id="login">login</button>`;
  document.getElementById('logout')?.addEventListener('click', () => {
    token = '';
    localStorage.removeItem('sf_token');
    renderAuth();
  });
  document.getElementById('login')?.addEventListener('click', async () => {
    const email = (document.getElementById('email') as HTMLInputElement).value;
    const pass = (document.getElementById('pass') as HTMLInputElement).value;
    const body = new URLSearchParams({ username: email, password: pass });
    const resp = await fetch(`${API}/auth/login`, { method: 'POST', body });
    const data = (await resp.json()) as TokenResponse;
    token = data.access_token;
    localStorage.setItem('sf_token', token);
    renderAuth();
    await loadStacks();
  });
}

async function loadStacks(): Promise<void> {
  if (!token) return;
  const resp = await fetch(`${API}/stacks`, { headers: headers() });
  const stacks = (await resp.json()) as Stack[];
  stackList.innerHTML = stacks.map(s => `
    <li>
      <span>${s.name} <small>${s.compose_path}</small></span>
      <button data-id="${s.id}" class="deploy">Deploy</button>
    </li>`).join('');
  stackList.querySelectorAll('.deploy').forEach(btn => {
    btn.addEventListener('click', () => deploy(Number((btn as HTMLButtonElement).dataset.id)));
  });
}

async function deploy(stackId: number): Promise<void> {
  logView.textContent = 'triggering deploy...\n';
  const resp = await fetch(`${API}/deployments/stack/${stackId}`, { method: 'POST', headers: headers() });
  const deployment = await resp.json();
  const ws = new WebSocket(`ws://localhost:8000/ws/deployments/${deployment.id}`);
  ws.onmessage = (ev) => { logView.textContent += ev.data; };
}

stackForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const name = (document.getElementById('stack-name') as HTMLInputElement).value;
  const compose_path = (document.getElementById('stack-path') as HTMLInputElement).value;
  await fetch(`${API}/stacks`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ name, compose_path }),
  });
  stackForm.reset();
  await loadStacks();
});

renderAuth();
loadStacks();
