import { useState, useEffect, useRef, useCallback } from "react";

// ── Wolfram rule engine ──────────────────────────────────────────────────────
function buildRule(n) {
  const bits = n.toString(2).padStart(8, "0");
  const map = {};
  ["111","110","101","100","011","010","001","000"].forEach((p, i) => {
    map[p] = parseInt(bits[i]);
  });
  return map;
}

function step(state, rule, boundary) {
  const n = state.length;
  return state.map((_, i) => {
    let l, r;
    if (boundary === "periodic") { l = state[(i-1+n)%n]; r = state[(i+1)%n]; }
    else if (boundary === "zero") { l = i > 0 ? state[i-1] : 0; r = i < n-1 ? state[i+1] : 0; }
    else { l = i > 0 ? state[i-1] : 1; r = i < n-1 ? state[i+1] : 1; }
    return rule[`${l}${state[i]}${r}`];
  });
}

function runCA(ruleNum, width, steps, initial, boundary) {
  const rule = buildRule(ruleNum);
  const grid = Array(steps + 1).fill(null).map(() => new Uint8Array(width));
  if (initial === "single") grid[0][Math.floor(width/2)] = 1;
  else { for (let i = 0; i < width; i++) grid[0][i] = Math.random() < 0.5 ? 1 : 0; }
  for (let t = 0; t < steps; t++) {
    const next = step(Array.from(grid[t]), rule, boundary);
    grid[t+1] = new Uint8Array(next);
  }
  return grid;
}

function coarseGrain(grid) {
  const rows = Math.floor(grid.length / 2) * 2;
  const cols = Math.floor(grid[0].length / 2) * 2;
  const out = [];
  for (let r = 0; r < rows; r += 2) {
    const row = new Uint8Array(cols / 2);
    for (let c = 0; c < cols; c += 2) {
      const sum = grid[r][c] + grid[r][c+1] + grid[r+1][c] + grid[r+1][c+1];
      row[c/2] = sum >= 2 ? 1 : 0;
    }
    out.push(row);
  }
  return out;
}

// ── Canvas renderer ──────────────────────────────────────────────────────────
function CACanvas({ grid, colors }) {
  const ref = useRef();
  useEffect(() => {
    if (!grid || !ref.current) return;
    const canvas = ref.current;
    const rows = grid.length, cols = grid[0].length;
    const cw = Math.max(1, Math.floor(canvas.width / cols));
    const ch = Math.max(1, Math.floor(canvas.height / rows));
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        ctx.fillStyle = grid[r][c] ? colors[1] : colors[0];
        ctx.fillRect(c * cw, r * ch, cw, ch);
      }
    }
  }, [grid, colors]);
  return <canvas ref={ref} width={480} height={380}
    style={{ width: "100%", height: "100%", display: "block", borderRadius: 4 }} />;
}

// ── Rule preview strip ───────────────────────────────────────────────────────
function RulePreview({ ruleNum, colors }) {
  const rule = buildRule(ruleNum);
  const patterns = ["111","110","101","100","011","010","001","000"];
  return (
    <div style={{ display:"flex", gap:4, justifyContent:"center", flexWrap:"wrap" }}>
      {patterns.map(p => (
        <div key={p} style={{ display:"flex", flexDirection:"column", alignItems:"center", gap:2 }}>
          <div style={{ display:"flex", gap:1 }}>
            {p.split("").map((b,i) => (
              <div key={i} style={{
                width:12, height:12, borderRadius:2,
                background: b==="1" ? colors[1] : colors[0],
                border: `1px solid ${colors[1]}33`
              }} />
            ))}
          </div>
          <div style={{
            width:12, height:12, borderRadius:2,
            background: rule[p] ? colors[1] : colors[0],
            border: `1px solid ${colors[1]}66`
          }} />
        </div>
      ))}
    </div>
  );
}

// ── Wolfram class labels ─────────────────────────────────────────────────────
const FAMOUS = {
  0:"Mort total",30:"Caòtica (PRNG)",90:"Fractal (Sierpiński)",
  110:"Turing-complet",184:"Trànsit",18:"Fractal",
  126:"Simètrica",150:"Additiva XOR",
};

function classLabel(n) {
  if ([0,8,32,40,128,136,160,168,255].includes(n)) return "Classe I – Estàtica";
  if ([4,108,218,232].includes(n)) return "Classe II – Periòdica";
  if ([30,45,73,89,109,124,193].includes(n)) return "Classe III – Caòtica";
  if ([110,124].includes(n)) return "Classe IV – Complexa";
  return "—";
}

// ── Color themes ─────────────────────────────────────────────────────────────
const THEMES = [
  { name:"Clàssic",   bg:"#0a0a0f", colors:["#0a0a0f","#e8e8f0"], accent:"#7b8cde" },
  { name:"Flama",     bg:"#0f0800", colors:["#0f0800","#ff6b1a"], accent:"#ffaa44" },
  { name:"Bosc",      bg:"#050f05", colors:["#050f05","#4caf50"], accent:"#81c784" },
  { name:"Glacial",   bg:"#030a14", colors:["#030a14","#4fc3f7"], accent:"#81d4fa" },
  { name:"Rosa",      bg:"#0f0510", colors:["#0f0510","#e91e8c"], accent:"#f06292" },
];

// ── Main component ───────────────────────────────────────────────────────────
export default function WolframExplorer() {
  const [ruleNum, setRuleNum] = useState(30);
  const [width, setWidth] = useState(120);
  const [steps, setSteps] = useState(100);
  const [boundary, setBoundary] = useState("periodic");
  const [initial, setInitial] = useState("single");
  const [themeIdx, setThemeIdx] = useState(0);
  const [showCoarse, setShowCoarse] = useState(false);
  const [grid, setGrid] = useState(null);
  const [coarse, setCoarse] = useState(null);

  const theme = THEMES[themeIdx];

  const generate = useCallback(() => {
    const g = runCA(ruleNum, width, steps, initial, boundary);
    setGrid(g);
    setCoarse(coarseGrain(g));
  }, [ruleNum, width, steps, boundary, initial]);

  useEffect(() => { generate(); }, [generate]);

  const displayGrid = showCoarse ? coarse : grid;

  const s = {
    wrap: {
      fontFamily:"'Courier New', monospace",
      background: theme.bg,
      color:"#ddd",
      minHeight:"100vh",
      padding:"16px",
      boxSizing:"border-box",
    },
    header: {
      textAlign:"center",
      marginBottom:12,
    },
    title: {
      fontSize:20,
      fontWeight:"bold",
      color: theme.accent,
      letterSpacing:2,
      textTransform:"uppercase",
    },
    sub: { fontSize:11, color:"#666", marginTop:2 },
    panel: {
      background:"#ffffff08",
      border:`1px solid ${theme.accent}22`,
      borderRadius:8,
      padding:"12px",
      marginBottom:10,
    },
    label: { fontSize:11, color: theme.accent, textTransform:"uppercase", letterSpacing:1, marginBottom:4, display:"block" },
    row: { display:"flex", gap:8, alignItems:"center", flexWrap:"wrap", marginBottom:6 },
    input: {
      background:"#ffffff0f",
      border:`1px solid ${theme.accent}44`,
      color:"#eee",
      borderRadius:4,
      padding:"4px 8px",
      fontSize:13,
      fontFamily:"inherit",
      outline:"none",
    },
    btn: (active=false) => ({
      background: active ? theme.accent : "#ffffff0f",
      border:`1px solid ${theme.accent}66`,
      color: active ? theme.bg : "#ccc",
      borderRadius:4,
      padding:"4px 10px",
      fontSize:12,
      cursor:"pointer",
      fontFamily:"inherit",
      transition:"all 0.15s",
    }),
    bigBtn: {
      background: theme.accent,
      border:"none",
      color: theme.bg,
      borderRadius:6,
      padding:"8px 20px",
      fontSize:13,
      fontWeight:"bold",
      cursor:"pointer",
      fontFamily:"inherit",
      letterSpacing:1,
    },
    ruleBig: {
      fontSize:48,
      fontWeight:"bold",
      color: theme.accent,
      lineHeight:1,
    },
    stat: { fontSize:11, color:"#888", marginTop:2 },
    canvasWrap: {
      background:"#000",
      borderRadius:6,
      overflow:"hidden",
      border:`1px solid ${theme.accent}33`,
      aspectRatio:"480/380",
    },
    tag: {
      display:"inline-block",
      background:`${theme.accent}22`,
      border:`1px solid ${theme.accent}44`,
      color: theme.accent,
      borderRadius:12,
      padding:"2px 8px",
      fontSize:10,
      marginLeft:8,
    },
  };

  return (
    <div style={s.wrap}>
      <div style={s.header}>
        <div style={s.title}>🔲 Autòmat Cel·lular de Wolfram</div>
        <div style={s.sub}>Sessió 1 · Regles elementals 1D</div>
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10 }}>
        {/* Left controls */}
        <div>
          {/* Rule selector */}
          <div style={s.panel}>
            <span style={s.label}>Número de Regla</span>
            <div style={{ display:"flex", alignItems:"center", gap:12, marginBottom:8 }}>
              <div style={s.ruleBig}>{ruleNum}</div>
              <div>
                <div style={{ fontSize:10, color:"#888" }}>{classLabel(ruleNum)}</div>
                {FAMOUS[ruleNum] && <div style={s.tag}>{FAMOUS[ruleNum]}</div>}
              </div>
            </div>
            <input type="range" min={0} max={255} value={ruleNum}
              onChange={e => setRuleNum(+e.target.value)}
              style={{ width:"100%", accentColor: theme.accent, marginBottom:6 }}
            />
            <div style={s.row}>
              {[0,30,90,110,184,126].map(r => (
                <button key={r} style={s.btn(ruleNum===r)} onClick={() => setRuleNum(r)}>{r}</button>
              ))}
            </div>
            <RulePreview ruleNum={ruleNum} colors={theme.colors} />
          </div>

          {/* Parameters */}
          <div style={s.panel}>
            <span style={s.label}>Paràmetres</span>
            <div style={s.row}>
              <span style={{ fontSize:11, color:"#888", width:60 }}>Amplada</span>
              <input type="number" min={20} max={300} value={width} style={{...s.input, width:60}}
                onChange={e => setWidth(Math.max(20, Math.min(300, +e.target.value)))} />
            </div>
            <div style={s.row}>
              <span style={{ fontSize:11, color:"#888", width:60 }}>Passos</span>
              <input type="number" min={20} max={300} value={steps} style={{...s.input, width:60}}
                onChange={e => setSteps(Math.max(20, Math.min(300, +e.target.value)))} />
            </div>
            <div style={s.row}>
              <span style={{ fontSize:11, color:"#888", width:60 }}>Frontera</span>
              {["periodic","zero","one"].map(b => (
                <button key={b} style={s.btn(boundary===b)} onClick={() => setBoundary(b)}>{b}</button>
              ))}
            </div>
            <div style={s.row}>
              <span style={{ fontSize:11, color:"#888", width:60 }}>Inici</span>
              {["single","random"].map(ic => (
                <button key={ic} style={s.btn(initial===ic)} onClick={() => setInitial(ic)}>{ic}</button>
              ))}
            </div>
          </div>

          {/* View toggle */}
          <div style={s.panel}>
            <span style={s.label}>Vista</span>
            <div style={s.row}>
              <button style={s.btn(!showCoarse)} onClick={() => setShowCoarse(false)}>Original</button>
              <button style={s.btn(showCoarse)} onClick={() => setShowCoarse(true)}>Coarse-grain K=2</button>
            </div>
            {showCoarse && coarse && (
              <div style={s.stat}>
                Original: {grid.length}×{grid[0].length} → Coarse: {coarse.length}×{coarse[0].length}
              </div>
            )}
          </div>

          {/* Theme */}
          <div style={s.panel}>
            <span style={s.label}>Tema</span>
            <div style={s.row}>
              {THEMES.map((t, i) => (
                <button key={i} style={s.btn(themeIdx===i)} onClick={() => setThemeIdx(i)}>{t.name}</button>
              ))}
            </div>
          </div>
        </div>

        {/* Right: canvas + stats */}
        <div>
          <div style={s.canvasWrap}>
            {displayGrid && <CACanvas grid={displayGrid} colors={theme.colors} />}
          </div>

          {grid && (
            <div style={{ ...s.panel, marginTop:10 }}>
              <span style={s.label}>Estadístiques</span>
              <div style={{ fontSize:11, color:"#aaa", lineHeight:1.8 }}>
                <div>Densitat (ρ): <span style={{ color: theme.accent }}>
                  {(grid.reduce((s,r) => s + Array.from(r).reduce((a,b)=>a+b,0), 0) / (grid.length * grid[0].length)).toFixed(4)}
                </span></div>
                {coarse && <div>Densitat coarse: <span style={{ color: theme.accent }}>
                  {(coarse.reduce((s,r) => s + Array.from(r).reduce((a,b)=>a+b,0), 0) / (coarse.length * coarse[0].length)).toFixed(4)}
                </span></div>}
                <div>Cèl·les: <span style={{ color:"#ccc" }}>{grid[0].length} × {grid.length}</span></div>
                <div>Regla (binari): <span style={{ color:"#ccc", letterSpacing:2 }}>{ruleNum.toString(2).padStart(8,"0")}</span></div>
              </div>
            </div>
          )}

          {/* Wolfram classes info */}
          <div style={{ ...s.panel, fontSize:10, color:"#666", lineHeight:1.7 }}>
            <span style={s.label}>Classes de Wolfram</span>
            <div>I – Estàtica (homogènia)</div>
            <div>II – Periòdica (estructures estables)</div>
            <div>III – Caòtica (ex: <span style={{color:theme.accent}}>Regla 30</span>)</div>
            <div>IV – Complexa (<span style={{color:theme.accent}}>Regla 110</span> → Turing-complet)</div>
          </div>
        </div>
      </div>
    </div>
  );
}
