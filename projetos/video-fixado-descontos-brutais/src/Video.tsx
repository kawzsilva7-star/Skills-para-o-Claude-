import React from "react";
import {
  AbsoluteFill, Audio, Img, Loop, OffthreadVideo, Sequence, interpolate, spring,
  staticFile, useCurrentFrame, useVideoConfig, Easing,
} from "remotion";
import { siTelegram, siWhatsapp, siTiktok, siInstagram } from "simple-icons";
import "@fontsource/poppins/700.css";
import "@fontsource/poppins/800.css";
import "@fontsource/poppins/900.css";
import "@fontsource/baloo-2/800.css";

type Versao = "instagram" | "outras";
const FPS = 30;
const f = (s: number) => Math.round(s * FPS);

const AMARELO = "#f2b300";
const TINTA = "#111";
const FONTE = "Poppins, sans-serif";
const BALAO = '"Baloo 2", Poppins, sans-serif';

// ---------- Tempos (segundos). s = início da cena; d = fala do dono; m = fala do mascote ----------
const T = {
  s1: 0, d1: 0.3,
  s2: 6.95, d2: 7.05,
  s3: 10.45, m1: 11.25,
  s4: 16.7, m2: 17.2,
  s5: 28.5, m3: 28.8,
  s6: 34.8, m4: 35.2,
  s7: 46.1, d3: 46.3, m5: 48.7,
  s8: 51.4, m6: 52.2,
  fim: 55.7,
};
export const TOTAL = f(T.fim);

// ---------- Legendas ----------
type Trecho = { t: string; ini: number; fim: number };
// divide a fala pelo tamanho do texto (quando a voz não tem pausas claras)
const fala = (ini: number, dur: number, partes: string[]): Trecho[] => {
  const total = partes.reduce((a, p) => a + p.length, 0);
  let acc = 0;
  return partes.map((p) => {
    const a = ini + (acc / total) * dur;
    acc += p.length;
    return { t: p, ini: a, fim: ini + (acc / total) * dur };
  });
};
// tempos medidos nas pausas da própria gravação
const em = (ini: number, partes: [string, number, number][]): Trecho[] =>
  partes.map(([t, a, b]) => ({ t, ini: ini + a, fim: ini + b }));

// *palavra* = etiqueta amarela
const LEGENDAS: Trecho[] = [
  ...em(T.d1, [["Poxa, eu queria comprar uma coisa,", 0.35, 3.3], ["mas queria achar um lugar", 3.43, 4.85], ["mais *barato* e *confiável*...", 4.85, 6.3]]),
  ...fala(T.d2, 2.9, ["Mas sempre dá medo", "de cair em *fraude*..."]),
  ...em(T.m1, [["Ei! Você poderia ficar no nosso", 0, 2.15], ["*grupo* de *ofertas*,", 2.15, 3.1], ["ou seguir a nossa página de *ofertas*!", 3.1, 5.1]]),
  ...em(T.m2, [
    ["Lá tem de tudo:", 0, 0.76], ["moda, beleza, academia,", 0.76, 2.78], ["cozinha, pet e muito mais!", 2.78, 4.3],
    ["Com *descontos*,", 4.42, 6.2], ["em lojas confiáveis,", 6.28, 8.6], ["*sem dor de cabeça*", 8.68, 9.85], ["de cair em fraude!", 9.85, 10.95],
  ]),
  ...em(T.m3, [["É só clicar no *link da bio*.", 0, 1.9], ["Lá estão *todos os produtos*", 2.0, 3.6], ["que já foram postados.", 3.6, 4.95]]),
  ...fala(T.m4, 10.4, ["E segue o nosso grupo do Telegram,", "nosso grupo do WhatsApp,", "nosso TikTok e nosso Instagram,", "pra ficar sempre informado", "das novas *promoções*, atualizações,", "*descontos* e *cupons*!"]),
  ...em(T.d3, [["Sério?", 0, 0.95], ["E quanto custa?", 1.0, 2.2]]),
  ...fala(T.m5, 2.5, ["*Não custa nada*", "e é *rapidinho*!"]),
];

const Legenda: React.FC<{ y: number }> = ({ y }) => {
  const frame = useCurrentFrame();
  const s = frame / FPS;
  const atual = LEGENDAS.find((l) => s >= l.ini && s < l.fim + 0.12);
  if (!atual) return null;
  const local = frame - f(atual.ini);
  const pop = spring({ frame: local, fps: FPS, config: { damping: 13, stiffness: 220, mass: 0.6 } });
  const partes = atual.t.split("*");
  return (
    <div style={{ position: "absolute", left: 70, right: 70, top: y, display: "flex", justifyContent: "center" }}>
      <div
        style={{
          fontFamily: FONTE, fontWeight: 900, fontSize: 54, lineHeight: 1.28, color: "#fff", textAlign: "center",
          textShadow: "0 0 14px rgba(0,0,0,.95), 0 4px 0 #000, 3px 0 0 #000, -3px 0 0 #000, 0 -3px 0 #000",
          transform: `scale(${interpolate(pop, [0, 1], [0.86, 1])})`, opacity: Math.min(1, local / 3 + 0.4), maxWidth: 900,
        }}
      >
        {partes.map((p, i) =>
          i % 2 === 1 ? (
            <span
              key={i}
              style={{
                background: AMARELO, color: TINTA, borderRadius: 16, padding: "2px 18px 4px", margin: "0 4px",
                textShadow: "none", display: "inline-block", boxShadow: "0 5px 0 rgba(0,0,0,.55)",
                transform: `scale(${interpolate(pop, [0, 1], [0.5, 1])}) rotate(-2deg)`,
              }}
            >
              {p}
            </span>
          ) : (
            <span key={i}>{p}</span>
          )
        )}
      </div>
    </div>
  );
};

// ---------- Balões (também usados nas etiquetas dos nichos) ----------
const Balao: React.FC<{
  texto: string; x: number; y: number; ini: number; fim: number; vermelho?: boolean; treme?: boolean; tam?: number; pensamento?: boolean;
}> = ({ texto, x, y, ini, fim, vermelho, treme, tam = 50, pensamento }) => {
  const frame = useCurrentFrame();
  const a = f(ini), b = f(fim);
  if (frame < a || frame > b + 9) return null;
  const entra = spring({ frame: frame - a, fps: FPS, config: { damping: 9, stiffness: 190, mass: 0.7 } });
  const sai = frame > b ? (frame - b) / 9 : 0;
  const flut = Math.sin((frame + x) / 11) * 7;
  const tremor = treme ? Math.sin(frame * 1.9 + x) * 4 : 0;
  const escala = entra * (1 + sai * 0.5);
  const cor = vermelho ? "#e02424" : AMARELO;
  return (
    <div
      style={{
        position: "absolute", left: x, top: y + flut,
        transform: `translate(-50%,-50%) translateX(${tremor}px) scale(${escala}) rotate(${Math.sin((frame + y) / 17) * 2.5}deg)`,
        opacity: 1 - sai,
      }}
    >
      <div
        style={{
          background: cor, color: vermelho ? "#fff" : TINTA, fontFamily: BALAO, fontWeight: 800, fontSize: tam,
          padding: "14px 34px 12px", borderRadius: 44, border: `5px solid ${vermelho ? "#7a0d0d" : "#111"}`,
          boxShadow: "0 10px 0 rgba(0,0,0,.45)", whiteSpace: "nowrap", lineHeight: 1.15,
        }}
      >
        {texto}
      </div>
      {pensamento ? (
        <>
          <div style={{ position: "absolute", left: "38%", bottom: -34, width: 30, height: 30, borderRadius: 30, background: cor, border: "4px solid #111" }} />
          <div style={{ position: "absolute", left: "30%", bottom: -62, width: 18, height: 18, borderRadius: 18, background: cor, border: "4px solid #111" }} />
        </>
      ) : null}
      {sai > 0
        ? [0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
            <div
              key={i}
              style={{
                position: "absolute", left: "50%", top: "50%", width: 16, height: 16, borderRadius: 16, background: cor,
                transform: `translate(-50%,-50%) rotate(${i * 45}deg) translateX(${80 + sai * 130}px)`,
              }}
            />
          ))
        : null}
    </div>
  );
};

// ---------- Fumaça da chegada ----------
const Fumaca: React.FC<{ x: number; y: number; ini: number }> = ({ x, y, ini }) => {
  const frame = useCurrentFrame() - f(ini);
  if (frame < 0 || frame > 26) return null;
  const p = frame / 26;
  return (
    <>
      {[0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => {
        const ang = (i / 9) * Math.PI * 2;
        const d = i === 0 ? 0 : 40 + p * 150;
        const r = (i === 0 ? 250 : 150) * (0.5 + p * 0.9);
        return (
          <div
            key={i}
            style={{
              position: "absolute", left: x + Math.cos(ang) * d, top: y + Math.sin(ang) * d, width: r, height: r, borderRadius: r,
              transform: "translate(-50%,-50%)", background: i % 2 ? "#ffd75a" : "#fff1b8",
              opacity: interpolate(p, [0, 0.45, 1], [1, 0.95, 0]), filter: "blur(6px)",
            }}
          />
        );
      })}
    </>
  );
};

// ---------- Dedo blocado ----------
const MAO = [
  "....XX......",
  "...XWWX.....",
  "...XWWX.....",
  "...XWWX.....",
  "...XWWXXX...",
  "...XWWXWWXX.",
  ".XXXWWXWWXWX",
  "XWWXWWWWWWWX",
  "XWWWWWWWWWWX",
  ".XWWWWWWWWWX",
  "..XWWWWWWWX.",
  "..XWWWWWWWX.",
  "...XWWWWWX..",
  "...XXXXXXX..",
];
const Mao: React.FC = () => {
  const px = 11;
  return (
    <div style={{ position: "relative", width: px * 12, height: px * 14, filter: "drop-shadow(0 8px 6px rgba(0,0,0,.5))" }}>
      {MAO.flatMap((lin, r) =>
        lin.split("").map((c, col) =>
          c === "." ? null : (
            <div key={`${r}-${col}`} style={{ position: "absolute", left: col * px, top: r * px, width: px + 0.5, height: px + 0.5, background: c === "X" ? "#111" : "#fff" }} />
          )
        )
      )}
    </div>
  );
};

type Passo = { t: number; x: number; y: number; toque?: boolean };
const Dedo: React.FC<{ passos: Passo[]; ini: number; fim: number }> = ({ passos, ini, fim }) => {
  const frame = useCurrentFrame();
  const s = frame / FPS;
  if (s < ini || s > fim) return null;
  const ts = passos.map((p) => p.t);
  const ease = { easing: Easing.inOut(Easing.cubic), extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
  const x = interpolate(s, ts, passos.map((p) => p.x), ease);
  const y = interpolate(s, ts, passos.map((p) => p.y), ease);
  const op = Math.min(1, (s - ini) * 5, (fim - s) * 5);
  const toques = passos.filter((p) => p.toque);
  const aperto = toques.reduce((m, p) => Math.max(m, 1 - Math.min(1, Math.abs(s - p.t) / 0.14)), 0);
  return (
    <>
      {toques.map((p, i) => {
        const d = s - p.t;
        if (d < 0 || d > 0.55) return null;
        const k = d / 0.55;
        return (
          <div
            key={i}
            style={{
              position: "absolute", left: p.x, top: p.y, width: 60 + k * 170, height: 60 + k * 170, borderRadius: 300,
              border: `10px solid ${AMARELO}`, transform: "translate(-50%,-50%)", opacity: 1 - k, boxShadow: "0 0 30px rgba(242,179,0,.8)",
            }}
          />
        );
      })}
      <div style={{ position: "absolute", left: x - 42, top: y - 6, opacity: op, transform: `scale(${1 - aperto * 0.14})`, transformOrigin: "40px 0" }}>
        <Mao />
      </div>
    </>
  );
};

// ---------- Cartão (pin) ----------
const PIN = { x: 200, y: 215, w: 680, h: 800 };
const Pin: React.FC<{ ini: number; fim: number; children: React.ReactNode; inclina?: number; lado?: 1 | -1 }> = ({ ini, fim, children, inclina = -2, lado = 1 }) => {
  const frame = useCurrentFrame();
  const a = f(ini), b = f(fim);
  if (frame < a || frame > b + 12) return null;
  const entra = spring({ frame: frame - a, fps: FPS, config: { damping: 11, stiffness: 170, mass: 0.8 } });
  const sai = frame > b ? interpolate(frame - b, [0, 12], [0, 1], { easing: Easing.in(Easing.cubic) }) : 0;
  const flut = Math.sin(frame / 19) * 9;
  return (
    <div
      style={{
        position: "absolute", left: PIN.x, top: PIN.y + flut, width: PIN.w, height: PIN.h, borderRadius: 44, overflow: "hidden",
        border: `6px solid ${AMARELO}`, background: "#000", boxShadow: "0 30px 70px rgba(0,0,0,.7), 0 0 50px rgba(242,179,0,.25)",
        transform: `translateX(${sai * 1200 * lado}px) scale(${entra}) rotate(${inclina + Math.sin(frame / 27) * 0.8 + sai * 10 * lado}deg)`,
      }}
    >
      {children}
    </div>
  );
};

// Página real (captura de docs/index.html, 860 px de largura) -> 668 no cartão
const K = 668 / 860;
const Site: React.FC<{ rolagem: (s: number) => number }> = ({ rolagem }) => {
  const s = useCurrentFrame() / FPS;
  return <Img src={staticFile("shots/site-full.png")} style={{ position: "absolute", left: 0, top: -rolagem(s) * 2 * K, width: 668 }} />;
};
const rolar = (pontos: [number, number][]) => (s: number) =>
  interpolate(s, pontos.map((p) => p[0]), pontos.map((p) => p[1]), {
    easing: Easing.inOut(Easing.cubic), extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

const Loja: React.FC = () => (
  <AbsoluteFill style={{ background: "#fff", color: "#111", fontFamily: FONTE }}>
    <div style={{ background: "#ffe600", padding: "22px 32px", fontWeight: 800, fontSize: 28 }}>Loja: Mercado Livre</div>
    <div style={{ padding: "22px 34px" }}>
      <div style={{ fontWeight: 700, fontSize: 32, lineHeight: 1.25 }}>Fatiador De Legumes Prático Para Cozinha</div>
      <Img src={staticFile("fatiador.jpg")} style={{ width: "100%", height: 400, objectFit: "contain", marginTop: 14 }} />
      <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 14 }}>
        <div style={{ fontSize: 24, color: "#666", fontWeight: 700 }}>Preço:</div>
        <div style={{ width: 190, height: 44, borderRadius: 10, background: "#cfcfcf", filter: "blur(5px)" }} />
      </div>
      <div style={{ marginTop: 20, background: "#3483fa", color: "#fff", textAlign: "center", fontWeight: 800, fontSize: 30, padding: "20px 0", borderRadius: 14 }}>
        Comprar agora
      </div>
    </div>
  </AbsoluteFill>
);

// ---------- Ícones das redes ----------
const Rede: React.FC<{ icone: { path: string }; cor: string; ini: number; de: [number, number]; para: [number, number]; fim: number }> = ({ icone, cor, ini, de, para, fim }) => {
  const frame = useCurrentFrame();
  const a = f(ini);
  if (frame < a || frame > f(fim) + 8) return null;
  const p = spring({ frame: frame - a, fps: FPS, config: { damping: 10, stiffness: 120, mass: 0.9 } });
  const sai = frame > f(fim) ? (frame - f(fim)) / 8 : 0;
  const x = interpolate(p, [0, 1], [de[0], para[0]]);
  const y = interpolate(p, [0, 1], [de[1], para[1]]) + Math.sin((frame + para[0]) / 10) * 8 - Math.sin(Math.min(1, p) * Math.PI) * 120;
  return (
    <div
      style={{
        position: "absolute", left: x, top: y, width: 124, height: 124, borderRadius: 124, background: cor, border: "6px solid #fff",
        transform: `translate(-50%,-50%) scale(${Math.min(1.15, p * 1.05) * (1 - sai)})`, display: "grid", placeItems: "center",
        boxShadow: "0 12px 0 rgba(0,0,0,.4), 0 0 30px rgba(0,0,0,.5)",
      }}
    >
      <svg viewBox="0 0 24 24" width={70} height={70}><path d={icone.path} fill="#fff" /></svg>
    </div>
  );
};

// ---------- Partículas ----------
const Vagalumes: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      {Array.from({ length: 16 }).map((_, i) => {
        const x = ((i * 197) % 1000) + 40 + Math.sin((frame + i * 40) / 50) * 26;
        const y = ((i * 331) % 1200) + 120 - ((frame * (0.25 + (i % 4) * 0.08)) % 160);
        return (
          <div key={i} style={{ position: "absolute", left: x, top: y, width: 9, height: 9, background: "#ffc45a", opacity: 0.35 + 0.45 * Math.abs(Math.sin((frame + i * 23) / 21)), boxShadow: "0 0 14px #ffb031" }} />
        );
      })}
    </>
  );
};

// ---------- Cenas 1 e 2: imagem do dono com zoom lento ----------
const DonoSozinho: React.FC = () => {
  const frame = useCurrentFrame();
  const s = frame / FPS;
  const zoom = interpolate(s, [0, T.s2, T.s2 + 0.9, T.s3], [1.04, 1.14, 1.42, 1.5], { easing: Easing.inOut(Easing.quad), extrapolateRight: "clamp" });
  const resp = Math.sin(frame / 22) * 5;
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#050a1c" }}>
      <Img src={staticFile("k1.png")} style={{ width: 1080, height: 1920, transform: `translateY(${resp}px) scale(${zoom})`, transformOrigin: "50% 41%" }} />
      <Vagalumes />
    </AbsoluteFill>
  );
};

// ---------- Tela final ----------
const Final: React.FC<{ versao: Versao }> = ({ versao }) => {
  const frame = useCurrentFrame() - f(T.s8);
  if (frame < 0) return null;
  const escuro = interpolate(frame, [0, 18], [0, 1], { extrapolateRight: "clamp" });
  const logo = spring({ frame: frame - 12, fps: FPS, config: { damping: 11, stiffness: 150 } });
  const txt = spring({ frame: frame - 24, fps: FPS, config: { damping: 14 } });
  const seta = spring({ frame: frame - 40, fps: FPS, config: { damping: 9 } });
  const brilho = 40 + Math.sin(frame / 7) * 22;
  const insta = versao === "instagram";
  return (
    <AbsoluteFill style={{ background: `rgba(0,0,0,${escuro})`, alignItems: "center", fontFamily: FONTE, color: "#fff" }}>
      <Img
        src={staticFile("logo.png")}
        style={{
          width: 430, height: 430, borderRadius: 430, objectFit: "cover", marginTop: 400, border: "6px solid #fff",
          boxShadow: `0 0 0 6px #000, 0 0 ${brilho + 40}px rgba(255,140,0,.9)`, transform: `scale(${logo})`,
        }}
      />
      <div style={{ fontWeight: 900, fontSize: 82, marginTop: 50, opacity: txt, transform: `translateY(${(1 - txt) * 40}px)` }}>
        Descontos Brutais <span style={{ color: AMARELO }}>⚡</span>
      </div>
      <div style={{ fontWeight: 700, fontSize: 48, color: "#cfcfcf", marginTop: 6, opacity: txt }}>@descontos_brutaiss</div>
      <div
        style={{
          marginTop: 60, background: AMARELO, color: TINTA, fontWeight: 900, fontSize: insta ? 54 : 46, padding: "20px 50px", borderRadius: 999,
          transform: `scale(${seta}) translateY(${Math.sin(frame / 6) * 8}px)`, boxShadow: "0 10px 0 rgba(255,255,255,.15)", whiteSpace: "nowrap",
        }}
      >
        {insta ? "👉 Clica no link da bio" : "👇 Clica no link aqui embaixo"}
      </div>
      <div style={{ position: "absolute", top: 1440, fontWeight: 700, fontSize: 30, color: "#9a9a9a", opacity: txt }}>Contém links de afiliado</div>
    </AbsoluteFill>
  );
};

// ---------- Áudio ----------
const Som: React.FC<{ arq: string; em: number; vol?: number }> = ({ arq, em: t, vol = 1 }) => (
  <Sequence from={f(t)} layout="none">
    <Audio src={staticFile(arq)} volume={vol} />
  </Sequence>
);

// Nichos da página (cena 4), no ritmo da fala: segundos depois do início da fala 2
const NICHOS: { t: number; texto: string; x: number; y: number }[] = [
  { t: 0.78, texto: "👗 Moda", x: 320, y: 300 },
  { t: 1.32, texto: "💄 Beleza", x: 750, y: 400 },
  { t: 1.82, texto: "🏋️ Academia", x: 420, y: 520 },
  { t: 2.8, texto: "🍳 Cozinha", x: 740, y: 640 },
  { t: 3.3, texto: "🐾 Pet", x: 330, y: 750 },
  { t: 3.6, texto: "✨ e muito mais!", x: 640, y: 860 },
];

export const Video: React.FC<{ versao?: Versao }> = ({ versao = "instagram" }) => {
  const frame = useCurrentFrame();
  const s = frame / FPS;
  const { durationInFrames } = useVideoConfig();

  // cena 4: etiquetas e depois a página
  const nichoSai = T.m2 + 4.3;
  const pin4 = T.m2 + 4.45;
  // cena 5: Instagram -> Beacons -> página -> loja
  const c5 = { insta: T.s5, link: T.s5 + 1.3, beacons: T.s5 + 1.7, ver: T.s5 + 2.75, pagina: T.s5 + 3.2, prod: T.s5 + 4.45, loja: T.s5 + 4.85 };
  // cena 6: toques nos botões das redes
  const t6 = { tg: T.m4 + 1.9, wa: T.m4 + 3.5, tk: T.m4 + 4.7, ig: T.m4 + 5.9 };
  // posição dos botões da página dentro do cartão (rolagem 300)
  const by = (cssY: number) => PIN.y + (cssY - 300) * 2 * K + 51;
  const bx = PIN.x + 340;

  // música: começa baixinha; recomeça na chegada do mascote (com o "puf") para terminar junto com o vídeo
  const MUSICA_CORTE = 4.8;
  const volIntro = (fr: number) => interpolate(fr / FPS, [0, T.s3 - 0.1, T.s3 + 0.2], [0.07, 0.07, 0], { extrapolateRight: "clamp" });
  const volMusica = (fr: number) => {
    const t = T.s3 + fr / FPS;
    if (t > T.s8 - 0.3) return interpolate(t, [T.s8 - 0.3, T.s8 + 0.8, T.fim - 1.2, T.fim], [0.085, 0.3, 0.3, 0], { extrapolateRight: "clamp" });
    return interpolate(t, [T.s3, T.s3 + 0.25, T.m1 - 0.1, T.m1 + 0.3], [0, 0.15, 0.15, 0.085], { extrapolateRight: "clamp" });
  };

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {/* ---------- Fundo ---------- */}
      <Sequence from={0} durationInFrames={f(T.s3)}><DonoSozinho /></Sequence>
      <Sequence from={f(T.s3)} durationInFrames={f(T.s4) - f(T.s3)}>
        <OffthreadVideo src={staticFile("clipB.mp4")} playbackRate={0.955} muted style={{ width: 1080, height: 1920 }} />
      </Sequence>
      <Sequence from={f(T.s4)} durationInFrames={f(T.s7) - f(T.s4)}>
        <Loop durationInFrames={f(7.9)}>
          <OffthreadVideo src={staticFile("clipC.mp4")} muted style={{ width: 1080, height: 1920 }} />
        </Loop>
      </Sequence>
      <Sequence from={f(T.s7)} durationInFrames={durationInFrames - f(T.s7)}>
        <OffthreadVideo src={staticFile("clipD.mp4")} playbackRate={0.85} muted style={{ width: 1080, height: 1920 }} />
      </Sequence>
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,.18) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 62%, rgba(0,0,0,.5) 100%)" }} />

      {/* ---------- Cena 1: pensamentos ---------- */}
      <Balao pensamento texto="Quero comprar..." x={540} y={420} ini={0.7} fim={2.5} />
      <Balao pensamento texto="...mas onde é mais barato?" x={540} y={420} ini={2.7} fim={4.7} tam={46} />
      <Balao pensamento texto="...e confiável?" x={540} y={420} ini={4.9} fim={6.75} />
      {/* ---------- Cena 2: dúvidas ---------- */}
      <Balao vermelho treme texto="Preço alto?" x={270} y={330} ini={T.s2 + 0.5} fim={T.s3 + 0.15} tam={46} />
      <Balao vermelho treme texto="Site falso?" x={800} y={300} ini={T.s2 + 1.2} fim={T.s3 + 0.25} tam={46} />
      <Balao vermelho treme texto="Fraude?" x={540} y={190} ini={T.s2 + 1.9} fim={T.s3 + 0.35} tam={52} />
      {/* ---------- Cena 3: chegada ---------- */}
      <Fumaca x={860} y={575} ini={T.s3} />
      <Balao texto="Calma! Eu te ajudo." x={470} y={330} ini={T.s3 + 0.7} fim={T.s3 + 3.4} tam={50} />

      {/* ---------- Cena 4: nichos e página de ofertas ---------- */}
      {NICHOS.map((n, i) => (
        <Balao key={n.texto} texto={n.texto} x={n.x} y={n.y} ini={T.m2 + n.t} fim={nichoSai + i * 0.07} tam={64} />
      ))}
      <Pin ini={pin4} fim={T.s5 - 0.35}>
        <Site rolagem={rolar([[pin4, 0], [T.m2 + 5.8, 0], [T.m2 + 7.3, 1530], [T.m2 + 8.9, 1530], [T.m2 + 9.8, 1780]])} />
      </Pin>
      <Dedo
        ini={T.m2 + 5.1} fim={T.s5 - 0.45}
        passos={[
          { t: T.m2 + 5.1, x: 780, y: 1010 }, { t: T.m2 + 5.75, x: 610, y: 820 }, { t: T.m2 + 7.3, x: 610, y: 380 },
          { t: T.m2 + 8.5, x: 640, y: 760 }, { t: T.m2 + 8.9, x: 640, y: 760 }, { t: T.m2 + 9.8, x: 640, y: 520 }, { t: T.s5 - 0.45, x: 760, y: 980 },
        ]}
      />

      {/* ---------- Cena 5: link da bio -> Beacons -> página -> loja ---------- */}
      <Pin ini={c5.insta} fim={c5.link + 0.3} inclina={2} lado={-1}>
        <Img src={staticFile("shots/insta.png")} style={{ width: 668 }} />
      </Pin>
      <Pin ini={c5.beacons} fim={c5.ver + 0.35} inclina={-2}>
        <Img src={staticFile("shots/beacons.png")} style={{ width: 668 }} />
      </Pin>
      <Pin ini={c5.pagina} fim={c5.prod + 0.3} inclina={2} lado={-1}>
        <Site rolagem={rolar([[c5.pagina + 0.2, 0], [c5.pagina + 0.8, 780]])} />
      </Pin>
      <Pin ini={c5.loja} fim={T.s6 - 0.3} inclina={-2}><Loja /></Pin>
      <Dedo
        ini={T.s5 + 0.5} fim={T.s6 - 0.6}
        passos={[
          { t: T.s5 + 0.5, x: 760, y: 980 }, { t: c5.link, x: 395, y: 536, toque: true }, { t: c5.link + 0.6, x: 600, y: 900 },
          { t: c5.ver, x: 540, y: 757, toque: true }, { t: c5.pagina + 0.15, x: 640, y: 900 }, { t: c5.pagina + 0.8, x: 640, y: 480 },
          { t: c5.prod, x: 520, y: 802, toque: true }, { t: T.s6 - 0.6, x: 720, y: 940 },
        ]}
      />

      {/* ---------- Cena 6: redes ---------- */}
      <Pin ini={T.s6} fim={T.s7 - 0.5}>
        <Site rolagem={rolar([[T.s6, 300]])} />
      </Pin>
      <Dedo
        ini={T.s6 + 0.5} fim={t6.ig + 0.9}
        passos={[
          { t: T.s6 + 0.5, x: 760, y: 1000 }, { t: t6.tg, x: bx, y: by(326), toque: true }, { t: t6.wa, x: bx, y: by(406), toque: true },
          { t: t6.tk, x: bx, y: by(486), toque: true }, { t: t6.ig, x: bx, y: by(566), toque: true }, { t: t6.ig + 0.9, x: 760, y: 980 },
        ]}
      />
      <Rede icone={siTelegram} cor="#229ED9" ini={t6.tg + 0.05} de={[bx, by(326)]} para={[630, 1275]} fim={T.s7 - 0.45} />
      <Rede icone={siWhatsapp} cor="#25D366" ini={t6.wa + 0.05} de={[bx, by(406)]} para={[765, 1300]} fim={T.s7 - 0.4} />
      <Rede icone={siTiktok} cor="#111" ini={t6.tk + 0.05} de={[bx, by(486)]} para={[900, 1275]} fim={T.s7 - 0.35} />
      <Rede icone={siInstagram} cor="#E1306C" ini={t6.ig + 0.05} de={[bx, by(566)]} para={[975, 1140]} fim={T.s7 - 0.3} />

      {/* ---------- Tela final e legendas ---------- */}
      <Final versao={versao} />
      {s < T.s8 + 0.3 ? <Legenda y={1385} /> : null}

      {/* ---------- Áudio ---------- */}
      <Sequence from={0} durationInFrames={f(T.s3 + 0.3)} layout="none">
        <Audio src={staticFile("musica.mp3")} volume={volIntro} />
      </Sequence>
      <Sequence from={f(T.s3)} layout="none">
        <Audio src={staticFile("musica.mp3")} trimBefore={f(MUSICA_CORTE)} volume={volMusica} />
      </Sequence>
      <Audio src={staticFile("ambiente.mp3")} volume={(fr) => (fr / FPS < T.s8 ? 0.8 : 0)} loop />
      <Som arq="dono-1b.mp3" em={T.d1} vol={1.9} />
      <Som arq="dono-2b.mp3" em={T.d2} vol={1.7} />
      <Som arq="masc-1a.mp3" em={T.m1} />
      <Som arq="masc-2n.mp3" em={T.m2} />
      <Som arq="masc-3a.mp3" em={T.m3} />
      <Som arq="masc-4a.mp3" em={T.m4} />
      <Som arq="dono-3b.mp3" em={T.d3} vol={1.5} />
      <Som arq="masc-5a.mp3" em={T.m5} />
      <Som arq={versao === "instagram" ? "masc-6a.mp3" : "masc-6o.mp3"} em={T.m6} />
      {[
        0.7, 2.7, 4.9, T.s2 + 0.5, T.s2 + 1.2, T.s2 + 1.9, T.s3 + 0.7,
        ...NICHOS.map((n) => T.m2 + n.t), pin4, c5.insta, c5.beacons, c5.pagina, c5.loja, T.s6,
        t6.tg + 0.05, t6.wa + 0.05, t6.tk + 0.05, t6.ig + 0.05,
      ].map((t, i) => (
        <Som key={`pop${i}`} arq="pop-2.mp3" em={t} vol={0.45} />
      ))}
      {[2.5, 4.7, 6.75, T.s3 + 0.15, T.s3 + 0.25, T.s3 + 0.35, T.s3 + 3.4, ...NICHOS.map((_, i) => nichoSai + i * 0.07)].map((t, i) => (
        <Som key={`plop${i}`} arq="plop-2.mp3" em={t} vol={1.6} />
      ))}
      <Som arq="puf-1.mp3" em={T.s3} vol={0.8} />
      {[c5.link, c5.ver, c5.prod, t6.tg, t6.wa, t6.tk, t6.ig].map((t, i) => (
        <Som key={`cl${i}`} arq="clique-2.mp3" em={t} vol={0.5} />
      ))}
    </AbsoluteFill>
  );
};
