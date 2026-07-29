import React, { useState, useEffect, useRef } from 'react';
import { 
  Layers, 
  Brain, 
  Sparkles, 
  Eye, 
  Activity, 
  BookOpen, 
  Compass, 
  Cpu, 
  UserCheck, 
  Quote, 
  Maximize2,
  Minimize2,
  Bookmark,
  Sliders,
  Focus,
  GitCommit,
  Network,
  X,
  Heart,
  ArrowRight,
  Sparkle,
  Mail,
  MailOpen,
  Copy,
  Check,
  Flower2
} from 'lucide-react';

export default function App() {
  const [inLandingView, setInLandingView] = useState(true);
  const [depthFilter, setDepthFilter] = useState(0);
  const [activeNode, setActiveNode] = useState(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [distortionLevel, setDistortionLevel] = useState(0.25);
  const [activeSankey, setActiveSankey] = useState(null);
  const [canvasScale, setCanvasScale] = useState(1);
  const [copiedCitation, setCopiedCitation] = useState(null);

  // Professor Digital Letter Modal State
  const [isLetterModalOpen, setIsLetterModalOpen] = useState(false);
  const [isLetterUnfolded, setIsLetterUnfolded] = useState(false);

  const heroCanvasRef = useRef(null);
  const workspaceCanvasRef = useRef(null);
  const lilacCanvasRef = useRef(null);

  // LANDING PAGE CANVAS SIMULATION (Full Blooming Bouquet Neural Mesh)
  useEffect(() => {
    if (!inLandingView) return;
    const canvas = heroCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    let width = (canvas.width = canvas.parentElement.clientWidth);
    let height = (canvas.height = 580);

    const handleResize = () => {
      if (!canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth;
      height = canvas.height = 580;
    };
    window.addEventListener('resize', handleResize);

    const particles = [];
    const numPoints = 2200;
    const cx = width * 0.5;
    const cy = height * 0.52;

    for (let i = 0; i < numPoints; i++) {
      const u = Math.random();
      const v = Math.random();
      const theta = u * Math.PI * 2;
      const phi = (v - 0.5) * Math.PI;

      const isStem = Math.random() < 0.12;

      let x, y, size, alpha;

      if (isStem) {
        x = cx + (Math.random() - 0.5) * 24 + Math.sin(v * 4) * 15;
        y = cy + 90 + Math.random() * 120;
        size = Math.random() * 1.4 + 0.4;
        alpha = Math.random() * 0.5 + 0.2;
      } else {
        const petalCount = 7;
        const layer = Math.floor(Math.random() * 4) + 1;
        const radiusScale = layer * 45 + Math.random() * 25;
        const r = radiusScale + 35 * Math.sin(theta * petalCount) * Math.cos(phi * 3);
        
        x = cx + r * Math.cos(theta) * Math.cos(phi * 0.6);
        y = cy + r * Math.sin(theta) * 0.85 + Math.sin(theta * 4) * 18;
        size = Math.random() * 2.0 + 0.6;
        alpha = Math.random() * 0.8 + 0.2;
      }

      particles.push({
        baseX: x,
        baseY: y,
        x: x,
        y: y,
        vx: 0,
        vy: 0,
        size: size,
        alpha: alpha,
        phase: Math.random() * Math.PI * 2,
        speed: Math.random() * 0.015 + 0.004
      });
    }

    let mouseX = -1000;
    let mouseY = -1000;

    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      mouseX = e.clientX - rect.left;
      mouseY = e.clientY - rect.top;
    };

    canvas.addEventListener('mousemove', handleMouseMove);

    let time = 0;
    const render = () => {
      time += 0.012;
      ctx.clearRect(0, 0, width, height);

      ctx.fillStyle = '#020203';
      ctx.fillRect(0, 0, width, height);

      ctx.fillStyle = 'rgba(255, 255, 255, 0.025)';
      const dotSpacing = 32;
      for (let x = 0; x < width; x += dotSpacing) {
        for (let y = 0; y < height; y += dotSpacing) {
          ctx.fillRect(x, y, 1.2, 1.2);
        }
      }

      particles.forEach((p, idx) => {
        p.phase += p.speed;

        const floatX = Math.sin(p.phase + time) * 2.2;
        const floatY = Math.cos(p.phase * 0.85 + time) * 2.2;

        const dx = mouseX - p.x;
        const dy = mouseY - p.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 150) {
          const force = (1 - dist / 150) * 40;
          const angle = Math.atan2(dy, dx);
          p.vx -= Math.cos(angle) * force * 0.1;
          p.vy -= Math.sin(angle) * force * 0.1;
        }

        p.vx += (p.baseX + floatX - p.x) * 0.04;
        p.vy += (p.baseY + floatY - p.y) * 0.04;

        p.vx *= 0.88;
        p.vy *= 0.88;

        p.x += p.vx;
        p.y += p.vy;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        const pulse = Math.sin(time * 2.5 + idx) * 0.3 + 0.7;
        ctx.fillStyle = `rgba(245, 247, 255, ${Math.min(1, p.alpha * pulse)})`;
        ctx.fill();
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      if (canvas) canvas.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, [inLandingView]);

  // MAIN WORKSPACE NEURAL BOUQUET SIMULATION
  useEffect(() => {
    if (inLandingView) return;
    const canvas = workspaceCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    let width = (canvas.width = canvas.parentElement.clientWidth);
    let height = (canvas.height = 520);

    const handleResize = () => {
      if (!canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth;
      height = canvas.height = 520;
    };
    window.addEventListener('resize', handleResize);

    const particles = [];
    const numPoints = 1800;
    const cx = width * 0.64;
    const cy = height * 0.5;

    for (let i = 0; i < numPoints; i++) {
      const u = Math.random();
      const v = Math.random();
      const theta = u * Math.PI * 2;
      const phi = (v - 0.5) * Math.PI;

      const isStem = Math.random() < 0.1;

      let x, y, size, alpha;

      if (isStem) {
        x = cx + (Math.random() - 0.5) * 20 + Math.sin(v * 3) * 12;
        y = cy + 80 + Math.random() * 100;
        size = Math.random() * 1.3 + 0.4;
        alpha = Math.random() * 0.5 + 0.2;
      } else {
        const petalCount = 7;
        const layer = Math.floor(Math.random() * 4) + 1;
        const radiusScale = layer * 38 + Math.random() * 20;
        const r = radiusScale + 30 * Math.sin(theta * petalCount) * Math.cos(phi * 3);
        
        x = cx + r * Math.cos(theta) * Math.cos(phi * 0.65);
        y = cy + r * Math.sin(theta) * 0.82 + Math.sin(theta * 4) * 15;
        size = Math.random() * 1.9 + 0.5;
        alpha = Math.random() * 0.75 + 0.25;
      }

      particles.push({
        baseX: x,
        baseY: y,
        x: x,
        y: y,
        vx: 0,
        vy: 0,
        size: size,
        alpha: alpha,
        phase: Math.random() * Math.PI * 2,
        speed: Math.random() * 0.015 + 0.005,
        neighbors: []
      });
    }

    for (let i = 0; i < particles.length; i++) {
      const p1 = particles[i];
      const dists = [];
      for (let j = 0; j < particles.length; j++) {
        if (i === j) continue;
        const p2 = particles[j];
        const dx = p1.baseX - p2.baseX;
        const dy = p1.baseY - p2.baseY;
        const d = dx * dx + dy * dy;
        if (d < 1100) dists.push({ idx: j, dist: d });
      }
      dists.sort((a, b) => a.dist - b.dist);
      p1.neighbors = dists.slice(0, 3).map(n => n.idx);
    }

    let mouseX = -1000;
    let mouseY = -1000;

    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      mouseX = e.clientX - rect.left;
      mouseY = e.clientY - rect.top;
      setMousePos({ x: Math.round(mouseX), y: Math.round(mouseY) });
    };

    canvas.addEventListener('mousemove', handleMouseMove);

    let time = 0;

    const neuralNodes = [
      { 
        id: 'cobb-guilt', 
        label: '01 // Cobb: Guilt Self-Schema', 
        x: cx - 120, 
        y: cy - 80,
        purpose: 'Enhancing understanding of internal guilt schemas.',
        concept: 'Reflected Appraisals & Shadow Self',
        filmScene: 'Mal invading Cobb\'s memory hotel room in the basement level.',
        detail: 'Cobb\'s identity is constructed around his perceived blame for Mal\'s death. Rather than facing reality directly, his self-concept is mediated through his projected memory of Mal. She acts as a harsh social mirror, perpetually reflecting his guilt back to his conscious mind.'
      },
      { 
        id: 'shared-architecture', 
        label: '02 // Ariadne: Dream Architecture', 
        x: cx + 20, 
        y: cy - 130,
        purpose: 'Mapping social constructivism in environmental design.',
        concept: 'Social Constructivism of Reality',
        filmScene: 'Ariadne folding the Paris streets over themselves.',
        detail: 'Inception demonstrates that reality is constructed through environment and social consensus. When Ariadne bends physics in the shared dream, she shows how malleable human beliefs become when environmental cues are systematically manipulated.'
      },
      { 
        id: 'fischer-locus', 
        label: '03 // Fischer: Locus of Control Shift', 
        x: cx + 110, 
        y: cy + 30,
        purpose: 'Visualizing cognitive re-engineering of agency.',
        concept: 'Internal vs External Locus of Control',
        filmScene: 'Fischer opening the snow fortress vault to find the paper windmill.',
        detail: 'Fischer begins with an external locus of control, feeling crushed under his father\'s empire. The team engineers a scenario where Fischer believes he is choosing to dissolve the company, shifting his locus from external pressure to internal agency.'
      },
      { 
        id: 'spotlight-leak', 
        label: '04 // The Spotlight Effect: Subconscious Leak', 
        x: cx - 70, 
        y: cy + 100,
        purpose: 'Exposing subconscious transparency distortions.',
        concept: 'Illusion of Transparency',
        filmScene: 'The freight train plowing through downtown traffic in Level 1.',
        detail: 'Cobb assumes his team can read his hidden guilt. Because he feels his emotional baggage is under an intense spotlight, his subconscious leaks physical obstacles into the shared dream, turning internal anxiety into environmental danger.'
      }
    ];

    const render = () => {
      time += 0.012;
      ctx.clearRect(0, 0, width, height);

      ctx.fillStyle = '#030305';
      ctx.fillRect(0, 0, width, height);

      ctx.strokeStyle = 'rgba(255, 255, 255, 0.025)';
      ctx.lineWidth = 1;
      const gridSize = 45;
      for (let x = 0; x < width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      particles.forEach((p) => {
        p.neighbors.forEach((nIdx) => {
          const np = particles[nIdx];
          const dx = p.x - np.x;
          const dy = p.y - np.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 45) {
            ctx.strokeStyle = `rgba(255, 255, 255, ${0.12 * (1 - dist / 45)})`;
            ctx.lineWidth = 0.5;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(np.x, np.y);
            ctx.stroke();
          }
        });
      });

      particles.forEach((p, idx) => {
        p.phase += p.speed;

        const floatX = Math.sin(p.phase + time) * 1.8;
        const floatY = Math.cos(p.phase * 0.9 + time) * 1.8;

        const dx = mouseX - p.x;
        const dy = mouseY - p.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 130) {
          const force = (1 - dist / 130) * 45 * distortionLevel;
          const angle = Math.atan2(dy, dx);
          p.vx -= Math.cos(angle) * force * 0.12;
          p.vy -= Math.sin(angle) * force * 0.12;
        }

        p.vx += (p.baseX + floatX - p.x) * 0.04;
        p.vy += (p.baseY + floatY - p.y) * 0.04;

        p.vx *= 0.86;
        p.vy *= 0.86;

        p.x += p.vx;
        p.y += p.vy;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        const pulse = Math.sin(time * 3 + idx) * 0.25 + 0.75;
        ctx.fillStyle = `rgba(250, 252, 255, ${Math.min(1, p.alpha * pulse)})`;
        ctx.fill();
      });

      neuralNodes.forEach((node) => {
        const isSelected = activeNode?.id === node.id;
        
        const dx = mouseX - node.x;
        const dy = mouseY - node.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 100) {
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
          ctx.setLineDash([2, 2]);
          ctx.beginPath();
          ctx.moveTo(node.x, node.y);
          ctx.lineTo(mouseX, mouseY);
          ctx.stroke();
          ctx.setLineDash([]);
        }

        ctx.beginPath();
        ctx.arc(node.x, node.y, isSelected ? 18 : 10, 0, Math.PI * 2);
        ctx.strokeStyle = isSelected ? '#ffffff' : 'rgba(255, 255, 255, 0.35)';
        ctx.lineWidth = isSelected ? 2 : 1;
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(node.x, node.y, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();

        ctx.font = '11px "Courier New", monospace';
        ctx.fillStyle = isSelected ? '#ffffff' : 'rgba(220, 220, 230, 0.7)';
        ctx.fillText(node.label, node.x + 18, node.y + 4);
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    const handleCanvasClick = (e) => {
      const rect = canvas.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const clickY = e.clientY - rect.top;

      const clicked = neuralNodes.find((node) => {
        const dx = clickX - node.x;
        const dy = clickY - node.y;
        return Math.sqrt(dx * dx + dy * dy) < 22;
      });

      if (clicked) {
        setActiveNode(clicked);
      }
    };

    canvas.addEventListener('click', handleCanvasClick);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (canvas) {
        canvas.removeEventListener('mousemove', handleMouseMove);
        canvas.removeEventListener('click', handleCanvasClick);
      }
      cancelAnimationFrame(animationFrameId);
    };
  }, [inLandingView, distortionLevel, activeNode]);

  // LILAC LILY BOUQUET PARTICLES FOR PROFESSOR ENVELOPE MODAL
  useEffect(() => {
    if (!isLetterModalOpen) return;
    const canvas = lilacCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    let width = (canvas.width = canvas.parentElement.clientWidth);
    let height = (canvas.height = 320);

    const handleResize = () => {
      if (!canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth;
      height = canvas.height = 320;
    };
    window.addEventListener('resize', handleResize);

    const particles = [];
    const numPoints = 1100;
    const cx = width * 0.5;
    const cy = height * 0.48;

    for (let i = 0; i < numPoints; i++) {
      const u = Math.random();
      const theta = u * Math.PI * 2;

      const isStem = Math.random() < 0.12;

      let x, y;
      if (isStem) {
        x = cx + (Math.random() - 0.5) * 16 + Math.sin(u * 10) * 8;
        y = cy + 50 + Math.random() * 80;
      } else {
        const r = (90 + 40 * Math.sin(theta * 6)) * Math.random();
        x = cx + r * Math.cos(theta);
        y = cy + r * Math.sin(theta);
      }

      particles.push({
        baseX: x,
        baseY: y,
        x: x,
        y: y,
        vx: 0,
        vy: 0,
        size: Math.random() * 2.2 + 0.7,
        color: i % 3 === 0 ? '#C8A2C8' : i % 3 === 1 ? '#D8B4E2' : '#E6E6FA',
        alpha: Math.random() * 0.85 + 0.15,
        phase: Math.random() * Math.PI * 2,
        speed: Math.random() * 0.02 + 0.005
      });
    }

    let mouseX = -1000;
    let mouseY = -1000;

    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      mouseX = e.clientX - rect.left;
      mouseY = e.clientY - rect.top;
    };

    canvas.addEventListener('mousemove', handleMouseMove);

    let time = 0;
    const render = () => {
      time += 0.015;
      ctx.clearRect(0, 0, width, height);

      ctx.fillStyle = '#08050e';
      ctx.fillRect(0, 0, width, height);

      for (let i = 0; i < particles.length; i += 4) {
        const p1 = particles[i];
        for (let j = i + 1; j < particles.length; j += 12) {
          const p2 = particles[j];
          const dx = p1.x - p2.x;
          const dy = p1.y - p2.y;
          const d = dx * dx + dy * dy;
          if (d < 900) {
            ctx.strokeStyle = `rgba(200, 162, 200, ${0.15 * (1 - d / 900)})`;
            ctx.lineWidth = 0.5;
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        }
      }

      particles.forEach((p) => {
        p.phase += p.speed;

        const floatX = Math.sin(p.phase + time) * 1.5;
        const floatY = Math.cos(p.phase * 0.9 + time) * 1.5;

        const dx = mouseX - p.x;
        const dy = mouseY - p.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 100) {
          const force = (1 - dist / 100) * 25;
          const angle = Math.atan2(dy, dx);
          p.vx -= Math.cos(angle) * force * 0.1;
          p.vy -= Math.sin(angle) * force * 0.1;
        }

        p.vx += (p.baseX + floatX - p.x) * 0.04;
        p.vy += (p.baseY + floatY - p.y) * 0.04;

        p.vx *= 0.88;
        p.vy *= 0.88;

        p.x += p.vx;
        p.y += p.vy;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.alpha;
        ctx.fill();
        ctx.globalAlpha = 1.0;
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      if (canvas) canvas.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, [isLetterModalOpen]);

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedCitation(id);
    setTimeout(() => setCopiedCitation(null), 2500);
  };

  // LANDING PAGE VIEW
  if (inLandingView) {
    return (
      <div className="min-h-screen bg-[#020203] text-neutral-200 font-sans relative overflow-hidden flex flex-col justify-between selection:bg-neutral-800 selection:text-white">
        
        {/* Top Header Navigation */}
        <header className="relative z-20 max-w-7xl mx-auto w-full px-6 py-6 flex items-center justify-between font-mono text-xs">
          <div className="flex items-center space-x-3">
            <span className="h-6 w-6 rounded-md bg-white text-black font-black flex items-center justify-center text-sm">F</span>
            <span className="font-bold text-white tracking-widest uppercase">Final Project</span>
          </div>
        </header>

        {/* Center Hero Content */}
        <main className="relative z-20 max-w-4xl mx-auto text-center px-6 my-auto pt-4 pb-8">
          <h1 className="text-4xl sm:text-6xl md:text-7xl font-light font-serif text-white tracking-tight leading-[1.15] mb-6">
            GNED-135 MOVIE ANALYSIS <br />
            <span className="font-bold italic">BY ANNA SHAHED</span>
          </h1>

          <p className="max-w-2xl mx-auto text-neutral-400 text-sm sm:text-base font-sans leading-relaxed mb-8">
            An interactive socio-psychological framework analyzing Christopher Nolan's <em>Inception</em> through the lens of David G. Myers' <em>Social Psychology (10th Edition)</em>.
          </p>

          {/* Action Button */}
          <div className="flex justify-center items-center">
            <button
              onClick={() => setInLandingView(false)}
              className="group relative px-8 py-4 rounded-2xl bg-white/10 border border-white/25 text-white font-mono text-sm tracking-wider uppercase transition-all duration-300 hover:bg-white hover:text-black shadow-2xl backdrop-blur-xl flex items-center gap-3 overflow-hidden"
            >
              <span className="relative z-10 font-bold">Begin Exploration</span>
              <ArrowRight className="w-4 h-4 relative z-10 transition-transform group-hover:translate-x-1" />
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
            </button>
          </div>
        </main>

        {/* Hero Interactive Canvas */}
        <div className="absolute inset-0 z-10 pointer-events-auto">
          <canvas ref={heroCanvasRef} className="w-full h-full block" />
        </div>

        {/* Landing Page Footer */}
        <footer className="relative z-20 max-w-7xl mx-auto w-full px-6 py-5 flex items-center justify-between text-xs font-mono text-neutral-500 border-t border-white/10">
          <div>GNED-135 Movie Analysis</div>
          <div className="flex items-center gap-2">
            <span>HANDMADE</span>
          </div>
        </footer>

      </div>
    );
  }

  // MAIN WORKSPACE VIEW
  return (
    <div className="min-h-screen bg-[#030305] text-neutral-200 font-sans relative overflow-x-hidden selection:bg-neutral-800 selection:text-white">
      
      {/* Background glow */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[500px] bg-gradient-to-b from-neutral-800/15 via-transparent to-transparent pointer-events-none blur-3xl z-0" />

      {/* Main Workspace Container */}
      <div className="relative z-10 max-w-[1500px] mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col min-h-screen">
        
        {/* Header Bar */}
        <header className="border border-white/10 bg-black/80 backdrop-blur-2xl rounded-2xl p-4 mb-6 flex flex-wrap items-center justify-between gap-4 shadow-2xl">
          <div className="flex items-center space-x-4">
            <button 
              onClick={() => setInLandingView(true)}
              className="h-10 w-10 rounded-xl bg-white text-black font-mono font-black text-xl flex items-center justify-center tracking-tighter shadow-lg hover:bg-neutral-200 transition-colors"
              title="Return to Landing Page"
            >
              α
            </button>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-[10px] uppercase tracking-widest text-neutral-400 font-mono">GNED-135 FINAL PROJECT</span>
              </div>
              <h1 className="text-lg sm:text-xl font-bold tracking-tight text-white flex items-center gap-2 font-serif">
                Inception: Socio-Psychological Neural Architecture
              </h1>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-3 text-xs font-mono">
            <div className="hidden lg:flex items-center bg-neutral-900/80 border border-white/10 rounded-xl p-1">
              <button
                onClick={() => setDepthFilter(0)}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  depthFilter === 0
                    ? 'bg-white text-black font-bold shadow'
                    : 'text-neutral-400 hover:text-white'
                }`}
              >
                All Layers
              </button>
              <button
                onClick={() => setDepthFilter(1)}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  depthFilter === 1
                    ? 'bg-white text-black font-bold shadow'
                    : 'text-neutral-400 hover:text-white'
                }`}
              >
                L1: Blueprint
              </button>
              <button
                onClick={() => setDepthFilter(2)}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  depthFilter === 2
                    ? 'bg-white text-black font-bold shadow'
                    : 'text-neutral-400 hover:text-white'
                }`}
              >
                L2: Matrix
              </button>
              <button
                onClick={() => setDepthFilter(3)}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  depthFilter === 3
                    ? 'bg-white text-black font-bold shadow'
                    : 'text-neutral-400 hover:text-white'
                }`}
              >
                L3: Digital Echo
              </button>
            </div>

            <button
              onClick={() => setInLandingView(true)}
              className="p-2.5 rounded-xl bg-neutral-900 border border-white/10 text-neutral-300 hover:text-white transition-colors font-mono text-xs flex items-center gap-2"
            >
              <span>LANDING PAGE</span>
            </button>

            <button
              onClick={() => setCanvasScale(canvasScale === 1 ? 0.95 : 1)}
              className="p-2.5 rounded-xl bg-neutral-900 hover:bg-neutral-800 border border-white/10 text-neutral-300 transition-colors"
            >
              {canvasScale === 1 ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
          </div>
        </header>

        {/* HERO NEURAL BOUQUET CANVAS */}
        <div className="mb-8 bg-neutral-950/80 border border-white/10 rounded-3xl overflow-hidden shadow-2xl relative">
          
          <div className="absolute top-4 left-4 right-4 z-20 flex justify-between items-center text-xs font-mono">
            <div className="flex items-center gap-3 bg-black/80 backdrop-blur-md px-3.5 py-1.5 rounded-full border border-white/10 text-neutral-300">
              <Network className="w-3.5 h-3.5 text-white animate-pulse" />
              <span>ORGANIC NEURAL BOUQUET SIMULATION</span>
              <span className="text-neutral-600">|</span>
              <span className="text-neutral-400">X: {mousePos.x} Y: {mousePos.y}</span>
            </div>

            <div className="flex items-center gap-2 bg-black/80 backdrop-blur-md px-3.5 py-1.5 rounded-full border border-white/10">
              <Sliders className="w-3.5 h-3.5 text-neutral-400" />
              <span className="text-neutral-400 text-[10px]">DISPERSION</span>
              <input 
                type="range" 
                min="0.05" 
                max="0.8" 
                step="0.05" 
                value={distortionLevel}
                onChange={(e) => setDistortionLevel(parseFloat(e.target.value))}
                className="w-20 h-1 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-white"
              />
            </div>
          </div>

          <div className="absolute left-6 top-20 max-w-xs z-20 hidden md:block pointer-events-none">
            <p className="font-serif text-2xl sm:text-3xl text-white leading-tight font-light">
              Enhancing Cognitive Comprehension.
            </p>
            <p className="text-xs text-neutral-400 mt-2 font-mono leading-relaxed">
              Click any neural node in the point cloud to inspect real-time socio-psychological citations and film scenes.
            </p>
          </div>

          <canvas 
            ref={workspaceCanvasRef} 
            className="w-full h-[500px] cursor-crosshair block relative z-10"
          />

          {/* Glass Pop-up Box */}
          {activeNode && (
            <div className="absolute right-6 top-16 w-80 sm:w-96 z-30 bg-black/75 backdrop-blur-xl border border-white/20 p-5 rounded-2xl shadow-2xl animate-fadeIn text-xs">
              <div className="flex justify-between items-start mb-3 border-b border-white/10 pb-2">
                <div className="flex items-center gap-2">
                  <GitCommit className="w-4 h-4 text-white" />
                  <span className="font-mono font-bold text-white uppercase">{activeNode.concept}</span>
                </div>
                <button 
                  onClick={() => setActiveNode(null)}
                  className="p-1 hover:bg-white/10 rounded-full text-neutral-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-3 font-sans">
                <div>
                  <span className="text-[10px] font-mono text-neutral-400 uppercase tracking-wider block mb-1">NODE PURPOSE:</span>
                  <p className="text-neutral-300 font-mono text-[11px] bg-white/5 p-2 rounded-md border border-white/5">
                    {activeNode.purpose}
                  </p>
                </div>

                <div>
                  <span className="text-[10px] font-mono text-neutral-400 uppercase tracking-wider block mb-1">SCENE REFERENCE:</span>
                  <p className="text-neutral-200 bg-neutral-900/80 p-2.5 rounded-lg border border-white/5 italic">
                    "{activeNode.filmScene}"
                  </p>
                </div>

                <div>
                  <span className="text-[10px] font-mono text-neutral-400 uppercase tracking-wider block mb-1">MYERS (2010) ANALYSIS:</span>
                  <p className="text-neutral-300 leading-relaxed">
                    {activeNode.detail}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Control Bar */}
          <div className="p-4 bg-black/90 border-t border-white/10 flex flex-wrap items-center justify-between gap-4 text-xs font-mono relative z-20">
            <div className="flex items-center gap-2 text-neutral-400">
              <Focus className="w-4 h-4 text-white" />
              <span>CLICK TO DISCOVER NODES:</span>
            </div>

            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setActiveNode(activeNode?.id === 'cobb-guilt' ? null : { 
                  id: 'cobb-guilt', 
                  purpose: 'Enhancing understanding of internal guilt schemas.',
                  concept: 'Reflected Appraisals & Shadow Self', 
                  filmScene: 'Mal invading Cobb\'s memory hotel room in the basement level.', 
                  detail: 'Cobb\'s identity is constructed around his perceived blame for Mal\'s death. Rather than facing reality directly, his self-concept is mediated through his projected memory of Mal. She acts as a harsh social mirror, perpetually reflecting his guilt back to his conscious mind.' 
                })}
                className="px-3 py-1.5 rounded-lg border bg-neutral-900 border-white/10 text-neutral-300 hover:border-white/30"
              >
                01 // Cobb's Schema
              </button>
              <button
                onClick={() => setActiveNode(activeNode?.id === 'shared-architecture' ? null : { 
                  id: 'shared-architecture', 
                  purpose: 'Mapping social constructivism in environmental design.',
                  concept: 'Social Constructivism of Reality', 
                  filmScene: 'Ariadne folding the Paris streets over themselves.', 
                  detail: 'Inception demonstrates that reality is constructed through environment and social consensus. When Ariadne bends physics in the shared dream, she shows how malleable human beliefs become when environmental cues are systematically manipulated.' 
                })}
                className="px-3 py-1.5 rounded-lg border bg-neutral-900 border-white/10 text-neutral-300 hover:border-white/30"
              >
                02 // Architecture
              </button>
              <button
                onClick={() => setActiveNode(activeNode?.id === 'fischer-locus' ? null : { 
                  id: 'fischer-locus', 
                  purpose: 'Visualizing cognitive re-engineering of agency.',
                  concept: 'Internal vs External Locus of Control', 
                  filmScene: 'Fischer opening the snow fortress vault to find the paper windmill.', 
                  detail: 'Fischer begins with an external locus of control, feeling crushed under his father\'s empire. The team engineers a scenario where Fischer believes he is choosing to dissolve the company, shifting his locus from external pressure to internal agency.' 
                })}
                className="px-3 py-1.5 rounded-lg border bg-neutral-900 border-white/10 text-neutral-300 hover:border-white/30"
              >
                03 // Fischer's Locus
              </button>
            </div>
          </div>
        </div>

        {/* INTERACTIVE CONNECTIONS VISUALIZER */}
        <div className="mb-8 bg-neutral-950/80 border border-white/10 rounded-3xl p-6 sm:p-8 relative overflow-hidden shadow-2xl">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 pb-4 border-b border-white/10 gap-4">
            <div>
              <div className="flex items-center gap-2 text-xs font-mono text-neutral-400 mb-1">
                <Activity className="w-4 h-4 text-white" />
                <span>DYNAMIC FLOW MAPPING</span>
              </div>
              <h3 className="text-xl font-bold font-serif text-white">
                Subconscious Flow & Conceptual Connections
              </h3>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-center my-4 font-mono text-xs relative">
            
            <div className="space-y-4">
              <div 
                onClick={() => setActiveSankey(activeSankey === 'input-1' ? null : 'input-1')}
                className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                  activeSankey === 'input-1' 
                    ? 'bg-white text-black border-white shadow-lg' 
                    : 'bg-neutral-900/90 border-white/10 text-neutral-300 hover:border-white/30'
                }`}
              >
                <div className="text-[10px] text-neutral-400 uppercase">35% INPUT</div>
                <div className="font-bold text-sm mt-0.5">Internal Remorse</div>
                <div className="text-[11px] mt-1 opacity-80">Cobb's Guilt Schema</div>
              </div>

              <div 
                onClick={() => setActiveSankey(activeSankey === 'input-2' ? null : 'input-2')}
                className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                  activeSankey === 'input-2' 
                    ? 'bg-white text-black border-white shadow-lg' 
                    : 'bg-neutral-900/90 border-white/10 text-neutral-300 hover:border-white/30'
                }`}
              >
                <div className="text-[10px] text-neutral-400 uppercase">65% INPUT</div>
                <div className="font-bold text-sm mt-0.5">External Locus</div>
                <div className="text-[11px] mt-1 opacity-80">Fischer's Inheritance</div>
              </div>
            </div>

            <div className="md:col-span-2 hidden md:block relative h-48">
              <svg className="w-full h-full overflow-visible" viewBox="0 0 400 180">
                <path 
                  d="M 10,40 C 180,40 220,140 390,140" 
                  fill="none" 
                  stroke={activeSankey === 'input-1' ? '#ffffff' : 'rgba(255, 255, 255, 0.15)'} 
                  strokeWidth={activeSankey === 'input-1' ? "4" : "2"}
                  className="transition-all duration-300"
                />
                <path 
                  d="M 10,40 C 180,40 220,40 390,40" 
                  fill="none" 
                  stroke={activeSankey === 'input-1' ? '#ffffff' : 'rgba(255, 255, 255, 0.2)'} 
                  strokeWidth={activeSankey === 'input-1' ? "4" : "2"}
                  className="transition-all duration-300"
                />
                <path 
                  d="M 10,140 C 180,140 220,40 390,40" 
                  fill="none" 
                  stroke={activeSankey === 'input-2' ? '#ffffff' : 'rgba(255, 255, 255, 0.15)'} 
                  strokeWidth={activeSankey === 'input-2' ? "4" : "2"}
                  className="transition-all duration-300"
                />
                <path 
                  d="M 10,140 C 180,140 220,140 390,140" 
                  fill="none" 
                  stroke={activeSankey === 'input-2' ? '#ffffff' : 'rgba(255, 255, 255, 0.25)'} 
                  strokeWidth={activeSankey === 'input-2' ? "4" : "2"}
                  className="transition-all duration-300"
                />
              </svg>
            </div>

            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-black/60 border border-white/10 text-neutral-300">
                <div className="text-[10px] text-neutral-400 uppercase">RESULTING CONCEPT</div>
                <div className="font-bold text-sm text-white mt-0.5">Reflected Appraisal</div>
                <div className="text-[11px] text-neutral-400 mt-1">Mal's Toxic Mirror</div>
              </div>

              <div className="p-4 rounded-2xl bg-black/60 border border-white/10 text-neutral-300">
                <div className="text-[10px] text-neutral-400 uppercase">RESULTING CONCEPT</div>
                <div className="font-bold text-sm text-white mt-0.5">Autonomous Epiphany</div>
                <div className="text-[11px] text-neutral-400 mt-1">Dissolving the Empire</div>
              </div>
            </div>

          </div>
        </div>

        {/* Dynamic Canvas Cards Layout */}
        <div 
          className="transition-all duration-300 ease-out flex-1 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-12"
          style={{ transform: `scale(${canvasScale})`, transformOrigin: 'top center' }}
        >

          {/* CARD 1: VISUAL BOARD TITLES & METADATA */}
          <div className="lg:col-span-3 bg-neutral-950/80 border border-white/10 rounded-3xl p-6 sm:p-8 relative overflow-hidden group hover:border-white/20 transition-all shadow-xl">
            <div className="flex flex-col lg:flex-row justify-between lg:items-center gap-6 pb-6 border-b border-white/10">
              <div className="space-y-2">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-neutral-900 border border-white/15 text-xs text-neutral-300 font-mono">
                  <BookOpen className="w-3.5 h-3.5 text-neutral-400" />
                  CHAPTER ANALYSIS: CH. 2 (THE SELF IN A SOCIAL WORLD)
                </div>
                <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight font-serif italic">
                  The Nested Self: Construction, Illusion & Inception
                </h2>
                <p className="text-neutral-400 text-sm max-w-3xl leading-relaxed">
                  An Academic Socio-Psychological Audit of Christopher Nolan's <span className="text-white italic">Inception</span> (2010), systematically grounded in the foundational paradigms of David G. Myers’ <span className="text-white">Social Psychology (10th Edition)</span>.
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 font-mono text-xs text-neutral-400">
                <div className="bg-black/60 border border-white/10 p-3.5 rounded-2xl min-w-[140px]">
                  <span className="block text-neutral-500 text-[10px] uppercase">PRIMARY TEXT</span>
                  <span className="text-white font-medium">Myers (2010)</span>
                </div>
                <div className="bg-black/60 border border-white/10 p-3.5 rounded-2xl min-w-[140px]">
                  <span className="block text-neutral-500 text-[10px] uppercase">SUBJECT FILM</span>
                  <span className="text-white font-medium">Inception (2010)</span>
                </div>
                <div className="bg-black/60 border border-white/10 p-3.5 rounded-2xl min-w-[140px]">
                  <span className="block text-neutral-500 text-[10px] uppercase">CORE THEME</span>
                  <span className="text-white font-medium">Social Constructivism</span>
                </div>
              </div>
            </div>

            {/* Vertical Layout Diagram */}
            <div className="mt-6 pt-2">
              <div className="text-xs font-mono uppercase tracking-widest text-neutral-400 mb-4 flex items-center gap-2">
                <Layers className="w-4 h-4 text-white" />
                NESTED DREAM LAYERS: THEORETICAL ARCHITECTURE
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                <div className="p-4 rounded-2xl bg-black/60 border border-white/10 flex items-start gap-3 hover:border-white/30 transition-all">
                  <span className="font-mono text-xs font-bold text-neutral-500">L1</span>
                  <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider font-mono">Subconscious Blueprint</h4>
                    <p className="text-[11px] text-neutral-400 mt-0.5">Shared Dreams & Extraction Mechanics</p>
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-black/60 border border-white/10 flex items-start gap-3 hover:border-white/30 transition-all">
                  <span className="font-mono text-xs font-bold text-neutral-400">L2</span>
                  <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider font-mono">Socio-Psych Matrix</h4>
                    <p className="text-[11px] text-neutral-400 mt-0.5">Reflected Appraisals & Control</p>
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-black/60 border border-white/10 flex items-start gap-3 hover:border-white/30 transition-all">
                  <span className="font-mono text-xs font-bold text-neutral-300">L3</span>
                  <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider font-mono">Digital Inception</h4>
                    <p className="text-[11px] text-neutral-400 mt-0.5">Algorithmic Echo Chambers & Feeds</p>
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-black/60 border border-white/10 flex items-start gap-3 hover:border-white/30 transition-all">
                  <span className="font-mono text-xs font-bold text-white">L4</span>
                  <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider font-mono">The Reality Anchor</h4>
                    <p className="text-[11px] text-neutral-400 mt-0.5">Lived Experience & Core Audit</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* CARD 2: CINEMATIC SUMMARY */}
          {(depthFilter === 0 || depthFilter === 1) && (
            <div className="lg:col-span-3 bg-neutral-950/80 border border-white/10 rounded-3xl p-6 sm:p-8 hover:border-white/20 transition-all shadow-xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4 border-b border-white/10 pb-3">
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-1 rounded-md bg-white text-black font-mono text-xs font-bold">
                      LAYER 1
                    </span>
                    <h3 className="text-sm font-semibold tracking-wider text-neutral-300 uppercase font-mono">
                      Cinematic Summary: The Subconscious Blueprint
                    </h3>
                  </div>
                  <Sparkles className="w-4 h-4 text-neutral-400" />
                </div>

                <div className="text-neutral-300 text-sm sm:text-base leading-relaxed space-y-4 font-normal">
                  <p className="first-letter:text-5xl first-letter:font-serif first-letter:font-bold first-letter:text-white first-letter:mr-3 first-letter:float-left">
                    Christopher Nolan’s <em>Inception</em> (2010) presents a sophisticated speculative framework where human subconsciousness is not an isolated sanctuary, but an architecturally editable, shared social landscape. The film follows Dom Cobb, a master "extractor" who infiltrates the target's dreamscapes via military-grade Pasiv tech to steal corporate trade secrets concealed deep within the ego’s defenses. However, extraction is eclipsed by the exponentially more volatile art of "inception" (the deliberate planting of an exogenous, self-replicating cognitive idea into a target’s subconscious mind such that they perceive it as their own organic epiphany). Operating within multi-layered dream architectures where subjective time expands exponentially, the team faces catastrophic psychological hazards: descending into "Limbo" (an unconstructed realm of raw, infinite subconsciousness that collapses one’s objective grasp of reality) and grappling with Cobb’s un-integrated guilt. Cobb’s tragic projection of his deceased wife, Mal, manifests as a destructive, autonomous shadow self that continually sabotages missions. To earn legal amnesty and reunite with his children in America, Cobb undertakes a high-stakes inception assignment targeting Robert Fischer, heir to a global energy conglomerate. By systematically constructing three nested dream layers, Cobb’s team manipulates Fischer’s unresolved Oedipal vulnerabilities, persuading him to autonomously dissolve his father’s monopolistic empire, thereby exposing how the core human self, its desires, and its choices are deeply malleable social constructs.
                  </p>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between text-xs text-neutral-400 font-mono">
                <span>MECHANICS: Shared Dreaming & Extraction</span>
                <span>TARGET: Robert Fischer</span>
              </div>
            </div>
          )}

          {/* CARD 3: SOCIO-PSYCHOLOGICAL MATRIX */}
          {(depthFilter === 0 || depthFilter === 2) && (
            <div className="lg:col-span-3 space-y-6">
              <div className="flex items-center space-x-2 border-b border-white/10 pb-3">
                <span className="px-2.5 py-1 rounded-md bg-white text-black font-mono text-xs font-bold">
                  LAYER 2
                </span>
                <h3 className="text-sm font-semibold tracking-wider text-neutral-300 uppercase font-mono">
                  Socio-Psychological Matrix (Lived Experiences in Shared Architecture)
                </h3>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Concept 1 */}
                <div className="bg-neutral-950/80 border border-white/10 rounded-3xl p-6 sm:p-7 hover:border-white/20 transition-all flex flex-col justify-between shadow-xl">
                  <div>
                    <div className="flex items-center space-x-2 text-white mb-3">
                      <Eye className="w-5 h-5 text-neutral-300" />
                      <h4 className="font-bold text-base tracking-tight font-serif italic">1. Looking-Glass Self & Reflected Appraisals</h4>
                    </div>
                    <div className="text-xs text-neutral-400 font-mono mb-4 pb-2 border-b border-white/10">
                      SUBJECT: Cobb & Mal Projection
                    </div>

                    <p className="text-neutral-300 text-xs sm:text-sm leading-relaxed space-y-3">
                      According to Charles Horton Cooley’s concept of the <em>looking-glass self</em>, as articulated by Myers (2010, p. 37), an individual’s self-concept is not constructed in vacuum isolation, but is instead derived through a perceived social mirror (specifically, how we imagine others perceive and evaluate us). In <em>Inception</em>, Dom Cobb’s internal self-schema is fatally compromised by this dynamic, manifested not through an actual living social network, but through his subconscious projection of his deceased wife, Mal. Cobb is trapped in a toxic loop of <em>reflected appraisals</em>: he continually sees himself through the imagined judgment of Mal, who perpetually accuses him of betraying her, breaking their vow to grow old together, and causing her suicide. Because Cobb harbors overwhelming real-world guilt for performing the initial inception on Mal that destroyed her perception of reality, his subconscious creates a monstrous, autonomous "looking-glass projection" of her. 
                      <br /><br />
                      This dream-projection functions as a punitive social mirror that repeatedly invades shared dream spaces to punish Cobb’s ego. Rather than maintaining an objective self-evaluation, Cobb allows his internal self-worth and identity to be defined by this imagined appraisal, proving Myers’ observation that "what matters for our self-concepts is not how others actually see us, but how we <em>imagine</em> they see us" (Myers, 2010, p. 38). Cobb’s sense of self becomes heavily fractured; he views himself as a murderer and a traitor because the projection of Mal incessantly mirrors that exact verdict back to his conscious mind.
                    </p>
                  </div>

                  <div className="mt-6 pt-3 border-t border-white/10 text-[11px] font-mono text-neutral-400">
                    Citations: Myers (2010, pp. 37-38)
                  </div>
                </div>

                {/* Concept 2 */}
                <div className="bg-neutral-950/80 border border-white/10 rounded-3xl p-6 sm:p-7 hover:border-white/20 transition-all flex flex-col justify-between shadow-xl">
                  <div>
                    <div className="flex items-center space-x-2 text-white mb-3">
                      <Activity className="w-5 h-5 text-neutral-300" />
                      <h4 className="font-bold text-base tracking-tight font-serif italic">2. The Spotlight Effect & Illusion of Transparency</h4>
                    </div>
                    <div className="text-xs text-neutral-400 font-mono mb-4 pb-2 border-b border-white/10">
                      SUBJECT: The Dream Leak Phenomenon
                    </div>

                    <p className="text-neutral-300 text-xs sm:text-sm leading-relaxed space-y-3">
                      Myers defines the <em>spotlight effect</em> as the tendency to overestimate the extent to which others notice and evaluate our appearance and behavior, while the <em>illusion of transparency</em> refers to the mistaken belief that our concealed internal emotions leak out and are easily readable by others (Myers, 2010, pp. 34-35). Within the shared dream architecture of <em>Inception</em>, these cognitive biases cease to be mere internal subjective distortions and become physicalized, catastrophic environmental phenomena known as "the dream leak." Cobb constantly labors under the paranoid belief that his intense, hidden remorse over Mal’s death is glaringly obvious to his teammates and will inevitably betray him. 
                      <br /><br />
                      Because the dream architecture is sustained by shared cognitive processing, Cobb’s egocentric belief that his psychological baggage is under a harsh spotlight actually causes his subconscious to manifest that baggage directly into the environment. When Cobb falsely assumes his internal emotional chaos is fully transparent to Ariadne or the rest of the team, his subconscious responds by leaking physical representations of his trauma (such as the train tearing through the city streets or Mal suddenly appearing in elevators). Cobb overestimates how much his team can read his mental state, yet by hyper-focusing on his guilt, he unconsciously projects it into the shared construct. The movie highlights how the illusion of transparency becomes a self-fulfilling prophecy: when an individual believes their internal vulnerabilities are glaringly exposed to their social group, their anxious overcompensation actively exposes those exact flaws to the surrounding world.
                    </p>
                  </div>

                  <div className="mt-6 pt-3 border-t border-white/10 text-[11px] font-mono text-neutral-400">
                    Citations: Myers (2010, pp. 34-36)
                  </div>
                </div>

                {/* Concept 3 */}
                <div className="bg-neutral-950/80 border border-white/10 rounded-3xl p-6 sm:p-7 hover:border-white/20 transition-all flex flex-col justify-between shadow-xl">
                  <div>
                    <div className="flex items-center space-x-2 text-white mb-3">
                      <Cpu className="w-5 h-5 text-neutral-300" />
                      <h4 className="font-bold text-base tracking-tight font-serif italic">3. Locus of Control & Self-Schema Engineering</h4>
                    </div>
                    <div className="text-xs text-neutral-400 font-mono mb-4 pb-2 border-b border-white/10">
                      SUBJECT: Inception of Robert Fischer
                    </div>

                    <p className="text-neutral-300 text-xs sm:text-sm leading-relaxed space-y-3">
                      Rotter’s concept of <em>locus of control</em> examines whether individuals perceive outcomes as internally controllable by their own efforts or externally controlled by chance or outside forces (Myers, 2010, p. 57). In <em>Inception</em>, Robert Fischer begins with a crippling, externally driven self-schema; his entire identity is dictated by an <em>external locus of control</em> centered around his domineering father, Maurice Fischer. Robert views himself as a perpetual disappointment, operating under the cognitive impression that his destiny is entirely controlled by his father's suffocating legacy and approval. Cobb’s team understands that to successfully perform inception, they cannot simply order Fischer to break up his father’s empire; doing so would trigger cognitive rejection as an external force. Instead, they must execute a radical re-engineering of Fischer’s self-schema by systematically shifting his locus of control from external to internal.
                      <br /><br />
                      Through three meticulously designed dream levels, the team reframes Maurice Fischer’s deathbed disappointment not as a cold rejection, but as an emotional plea for Robert to be his own man ("He was disappointed that I tried to be him"). By manipulating Fischer's emotional schemas, Cobb alters Fischer's perceived control orientation. When Fischer finally opens the vault in Level 3 and encounters his dying father holding the paper windmill from his childhood, Fischer experiences an internal cognitive epiphany. He shifts from an external victim of his father's empire to an empowered, autonomous agent who internalizes the choice to dissolve the conglomerate. By reprogramming Fischer's belief that breaking up the company is an act of authentic self-actualization, Cobb demonstrates how external social influences can stealthily alter an individual's internal locus of control and fundamentally reconfigure their core self-concept.
                    </p>
                  </div>

                  <div className="mt-6 pt-3 border-t border-white/10 text-[11px] font-mono text-neutral-400">
                    Citations: Myers (2010, pp. 57-59)
                  </div>
                </div>

              </div>
            </div>
          )}

          {/* CARD 4: DIGITAL INCEPTION */}
          {(depthFilter === 0 || depthFilter === 3) && (
            <div className="lg:col-span-3 bg-neutral-950/80 border border-white/10 rounded-3xl p-6 sm:p-8 hover:border-white/20 transition-all shadow-xl space-y-6">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <div className="flex items-center space-x-2">
                  <span className="px-2.5 py-1 rounded-md bg-white text-black font-mono text-xs font-bold">
                    LAYER 3: BONUS HIGHLIGHT
                  </span>
                  <h3 className="text-sm font-semibold tracking-wider text-neutral-300 uppercase font-mono">
                    Digital Inception: Algorithmic Echo Chambers & Synthetic Realities
                  </h3>
                </div>
                <Compass className="w-4 h-4 text-neutral-400" />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <h4 className="text-sm font-bold text-white flex items-center gap-2 font-serif">
                    <span className="w-2 h-2 rounded-full bg-white"></span>
                    Algorithms as Synthetic Dream Architects
                  </h4>
                  <p className="text-neutral-300 text-xs sm:text-sm leading-relaxed">
                    In contemporary digital environments, social media algorithms function as hyper-sophisticated, automated dream architects. Just as Cobb’s team constructs custom dream layers carefully designed around Robert Fischer’s implicit biases, childhood memories, and cognitive vulnerabilities, platform recommendation algorithms engineer individualized digital realities optimized for maximum psychological engagement. These predictive models analyze micro-interactions (dwell time, cursor pauses, emotional reactions, and search histories) to continuously tweak the user's information architecture. By curating a customized stream of outrage, validation, and targeted content, the algorithm constructs a synthetic informational bubble that mirrors and exaggerates the user’s internal anxieties and latent desires. The user inhabits an artificially constructed world where every feed update confirms their pre-existing worldview, echoing Cobb’s warning about dream spaces: the environment feels so real because the subconscious (or algorithmic profile) is actively constructing it in real-time as the user consumes it.
                  </p>
                </div>

                <div className="space-y-3">
                  <h4 className="text-sm font-bold text-white flex items-center gap-2 font-serif">
                    <span className="w-2 h-2 rounded-full bg-white"></span>
                    Distortion of the Looking-Glass Self
                  </h4>
                  <p className="text-neutral-300 text-xs sm:text-sm leading-relaxed">
                    Inhabiting an algorithmic echo chamber severely warps the user’s <em>looking-glass self</em> by providing a hyper-curated, highly distorted digital social mirror. In an unmediated physical world, reflected appraisals are tempered by heterogeneous social feedback, non-verbal nuance, and objective realities. However, within an algorithmic echo chamber, opposing viewpoints are systematically filtered out, while radical or self-confirming opinions are amplified through algorithmic reinforcement. The digital social mirror no longer reflects objective social consensus; instead, it offers a synthetic, highly inflated feedback loop. When a user sees their hyper-specific anxieties or ideological biases reflected back at them by thousands of algorithmic likes, retweets, or agreement comments, their self-concept becomes anchored to a manipulated baseline of social reality. Much like Mal losing her ability to distinguish dream from reality because her totem was altered, modern digital users lose their cognitive baseline for objective truth, believing that their hyper-curated echo chamber represents universal consensus.
                  </p>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-black/60 border border-white/10 font-mono text-xs text-neutral-400 flex items-center justify-between">
                <span>PARALLEL: Architectural Dream Logic & Platform Curation</span>
                <span className="text-white">Pariser (2011) / Myers (2010)</span>
              </div>
            </div>
          )}

          {/* CARD 5: THE REALITY ANCHOR */}
          {(depthFilter === 0 || depthFilter === 3) && (
            <div className="lg:col-span-2 bg-neutral-950/80 border border-white/10 rounded-3xl p-6 sm:p-8 hover:border-white/20 transition-all shadow-xl flex flex-col justify-between">
              <div>
                <div className="flex items-center space-x-2 mb-4 border-b border-white/10 pb-3">
                  <span className="px-2.5 py-1 rounded-md bg-white text-black font-mono text-xs font-bold">
                    LAYER 4
                  </span>
                  <h3 className="text-sm font-semibold tracking-wider text-neutral-300 uppercase font-mono">
                    The Reality Anchor: Personal Reflection on Digital Distortions
                  </h3>
                </div>

                <div className="relative pl-6 border-l-2 border-white/30 space-y-3 my-2">
                  <Quote className="w-6 h-6 text-neutral-400 absolute -top-2 -left-3 bg-[#030305] p-1" />
                  <p className="text-neutral-300 text-xs sm:text-sm leading-relaxed italic font-serif">
                    "During my undergraduate studies, I found myself quietly pulled down an intense online algorithmic rabbit hole centered around hyper-optimized productivity culture and elite athletic conditioning. What began as a harmless search for workout routines quickly mutated as platform algorithms flooded my feeds with extreme biohacking, rigid calorie tracking, and curated clips of individuals achieving unblemished corporate and athletic success. Within weeks, my looking-glass self was completely altered: I began measuring my personal self-worth against an impossible, algorithmically constructed standard of perfection. I suffered from an acute spotlight effect, convinced that peers in my social circles were evaluating my minor physical slumps or temporary productivity lapses. My locus of control felt increasingly external (feeling helpless against the relentless stream of content telling me I was underperforming). Breaking this digital inception required a deliberate, structural 'reality anchor.' I initiated a complete digital detox, uninstalled recommendation-heavy applications, and re-engaged in unfiltered physical community activities. By deliberately shattering the curated algorithmic feedback loop, I was able to dismantle the synthetic baseline of perfection, reclaim an internal locus of control, and restore an authentic self-schema grounded in physical reality."
                  </p>
                </div>
              </div>

              <div className="mt-6 pt-3 border-t border-white/10 flex items-center justify-between font-mono text-xs text-neutral-400">
                <span>FIRST-PERSON PHENOMENOLOGICAL AUDIT</span>
                <span>RECLAIMING INTERNAL LOCUS</span>
              </div>
            </div>
          )}

          {/* CARD 6: THE CORE AUDIT */}
          {(depthFilter === 0 || depthFilter === 3) && (
            <div className="lg:col-span-1 bg-neutral-950/80 border border-white/10 rounded-3xl p-6 sm:p-8 hover:border-white/20 transition-all shadow-xl flex flex-col justify-between">
              <div>
                <div className="flex items-center space-x-2 mb-4 border-b border-white/10 pb-3">
                  <span className="px-2.5 py-1 rounded-md bg-white text-black font-mono text-xs font-bold">
                    CORE AUDIT
                  </span>
                  <h3 className="text-sm font-semibold tracking-wider text-neutral-300 uppercase font-mono">
                    The Overarching Situation
                  </h3>
                </div>

                <p className="text-neutral-300 text-xs sm:text-sm leading-relaxed">
                  Ultimately, Christopher Nolan’s <em>Inception</em> serves as an illuminating, high-concept allegory for the foundational thesis of modern social psychology: the human self is never an isolated, sovereign island, but a deeply permeable construct continuously molded, co-constructed, and manipulated by immediate social situations and environmental contexts. As Myers (2010) repeatedly demonstrates throughout his work, our innermost self-schemas, perceived agency, and emotional convictions are systematically shaped by the subtle social forces surrounding us. Whether through the subconscious guilt projecting from a shared dream architecture or the invisible curation of modern algorithmic feeds, our sense of autonomy is far more vulnerable to external 'inceptions' than our conscious ego cares to admit. The film forces us to recognize that true psychological liberation requires constant vigilance over our environmental anchors, lest we mistake an engineered social construct for our own authentic reality.
                </p>
              </div>

              <div className="mt-6 pt-3 border-t border-white/10 text-[11px] font-mono text-neutral-400 flex items-center justify-between">
                <span>SOCIAL CONSTRUCTIVISM</span>
                <UserCheck className="w-4 h-4 text-white" />
              </div>
            </div>
          )}

          {/* CARD 7: ENHANCED ACADEMIC BIBLIOGRAPHY MATRIX */}
          <div className="lg:col-span-3 bg-neutral-950 border border-white/15 rounded-3xl p-6 sm:p-8 hover:border-white/30 transition-all shadow-2xl">
            <div className="flex items-center justify-between mb-6 border-b border-white/10 pb-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-xl bg-white/10 text-white">
                  <Bookmark className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold tracking-wider text-white uppercase font-mono">
                    ACADEMIC BIBLIOGRAPHY & CASE STUDY CITATIONS
                  </h3>
                  <p className="text-xs text-neutral-400 font-mono">APA 7th Edition Formal References</p>
                </div>
              </div>
              <span className="text-xs px-3 py-1 rounded-full bg-white/10 text-neutral-300 font-mono border border-white/10">3 VERIFIED SOURCES</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs text-neutral-300">
              
              {/* Citation 1 */}
              <div className="p-5 rounded-2xl bg-black/70 border border-white/10 flex flex-col justify-between space-y-4 hover:border-white/30 transition-all">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-[10px] text-neutral-400">
                    <span className="px-2 py-0.5 rounded bg-white/10 text-white font-bold">PRIMARY TEXTBOOK</span>
                    <span>Myers (2010)</span>
                  </div>
                  <p className="text-white font-medium leading-relaxed">
                    Myers, D. G. (2010). <em>Social Psychology</em> (10th ed.). McGraw-Hill Higher Education.
                  </p>
                </div>
                <button
                  onClick={() => copyToClipboard('Myers, D. G. (2010). Social Psychology (10th ed.). McGraw-Hill Higher Education.', 'myers')}
                  className="w-full py-2.5 rounded-xl bg-neutral-900 border border-white/10 text-neutral-300 hover:bg-white hover:text-black transition-all flex items-center justify-center gap-2 text-[11px] font-bold"
                >
                  {copiedCitation === 'myers' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedCitation === 'myers' ? 'CITATION COPIED' : 'COPY CITATION'}</span>
                </button>
              </div>

              {/* Citation 2 */}
              <div className="p-5 rounded-2xl bg-black/70 border border-white/10 flex flex-col justify-between space-y-4 hover:border-white/30 transition-all">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-[10px] text-neutral-400">
                    <span className="px-2 py-0.5 rounded bg-white/10 text-white font-bold">CINEMATIC CASE STUDY</span>
                    <span>Nolan (2010)</span>
                  </div>
                  <p className="text-white font-medium leading-relaxed">
                    Nolan, C. (Director). (2010). <em>Inception</em> [Motion picture]. Warner Bros. Pictures.
                  </p>
                </div>
                <button
                  onClick={() => copyToClipboard('Nolan, C. (Director). (2010). Inception [Motion picture]. Warner Bros. Pictures.', 'nolan')}
                  className="w-full py-2.5 rounded-xl bg-neutral-900 border border-white/10 text-neutral-300 hover:bg-white hover:text-black transition-all flex items-center justify-center gap-2 text-[11px] font-bold"
                >
                  {copiedCitation === 'nolan' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedCitation === 'nolan' ? 'CITATION COPIED' : 'COPY CITATION'}</span>
                </button>
              </div>

              {/* Citation 3 */}
              <div className="p-5 rounded-2xl bg-black/70 border border-white/10 flex flex-col justify-between space-y-4 hover:border-white/30 transition-all">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-[10px] text-neutral-400">
                    <span className="px-2 py-0.5 rounded bg-white/10 text-white font-bold">DIGITAL INCEPTION</span>
                    <span>Pariser (2011)</span>
                  </div>
                  <p className="text-white font-medium leading-relaxed">
                    Pariser, E. (2011). <em>The Filter Bubble: What the Internet Is Hiding from You</em>. Penguin Press.
                  </p>
                </div>
                <button
                  onClick={() => copyToClipboard('Pariser, E. (2011). The Filter Bubble: What the Internet Is Hiding from You. Penguin Press.', 'pariser')}
                  className="w-full py-2.5 rounded-xl bg-neutral-900 border border-white/10 text-neutral-300 hover:bg-white hover:text-black transition-all flex items-center justify-center gap-2 text-[11px] font-bold"
                >
                  {copiedCitation === 'pariser' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedCitation === 'pariser' ? 'CITATION COPIED' : 'COPY CITATION'}</span>
                </button>
              </div>

            </div>
          </div>

        </div>

        {/* SPECIAL DIGITAL ENVELOPE CARD */}
        <div className="mt-4 mb-8 bg-gradient-to-r from-purple-950/40 via-neutral-950 to-purple-950/40 border border-purple-500/30 rounded-3xl p-6 sm:p-8 relative overflow-hidden shadow-2xl">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="space-y-1 text-center sm:text-left">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 font-mono text-xs border border-purple-400/30 mb-2">
                <Flower2 className="w-3.5 h-3.5 text-purple-300 animate-pulse" />
                <span>INTERACTIVE ENVELOPE</span>
              </div>
              <h4 className="text-2xl font-serif text-white font-bold italic">
                A Special Digital Envelope
              </h4>
            </div>

            <button
              onClick={() => {
                setIsLetterModalOpen(true);
                setIsLetterUnfolded(false);
              }}
              className="px-8 py-4 rounded-2xl bg-purple-500/20 border border-purple-400/40 hover:bg-purple-300 hover:text-black transition-all duration-300 text-purple-200 font-mono text-xs tracking-wider uppercase flex items-center gap-3 shadow-xl backdrop-blur-md group"
            >
              <Mail className="w-4 h-4 text-purple-300 group-hover:text-black transition-colors" />
              <span className="font-bold">SEE MESSAGE</span>
            </button>
          </div>
        </div>

        {/* PROFESSOR DIGITAL LETTER MODAL OVERLAY */}
        {isLetterModalOpen && (
          <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-xl flex items-center justify-center p-4 sm:p-6 animate-fadeIn">
            <div className="bg-neutral-950 border border-purple-500/30 rounded-3xl max-w-2xl w-full overflow-hidden shadow-2xl relative flex flex-col">
              
              {/* Modal Top Bar */}
              <div className="p-4 bg-black/90 border-b border-white/10 flex justify-between items-center z-20 font-mono text-xs">
                <div className="flex items-center gap-2 text-purple-300">
                  <Flower2 className="w-4 h-4" />
                  <span>DIGITAL ENVELOPE // LILAC LILY NEURAL MATRIX</span>
                </div>
                <button
                  onClick={() => setIsLetterModalOpen(false)}
                  className="p-1.5 rounded-full hover:bg-white/10 text-neutral-400 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Lilac Lily Particle Canvas Header */}
              <div className="relative h-44 w-full overflow-hidden bg-[#08050e]">
                <canvas ref={lilacCanvasRef} className="w-full h-full block" />
                <div className="absolute inset-0 bg-gradient-to-t from-neutral-950 via-transparent to-transparent pointer-events-none" />
                <div className="absolute bottom-3 left-6 border border-purple-400/30 px-3 py-1 rounded-full font-mono text-xs text-purple-200 bg-purple-950/80">
                  INTERACTIVE FLOWER CANVAS
                </div>
              </div>

              {/* Envelope Unfolding Interface */}
              <div className="p-6 sm:p-8 space-y-6 font-sans">
                
                {!isLetterUnfolded ? (
                  <div className="text-center py-8 space-y-6">
                    <div className="w-20 h-20 mx-auto rounded-3xl bg-purple-500/20 border border-purple-400/40 flex items-center justify-center text-purple-300 shadow-2xl">
                      <MailOpen className="w-10 h-10 animate-bounce" />
                    </div>
                    <div className="space-y-2">
                      <h3 className="text-2xl font-serif text-white font-bold italic">A Special Digital Envelope</h3>
                      <p className="text-xs text-neutral-400 font-mono max-w-sm mx-auto">
                        Prepared for GNED-135 Movie Analysis.
                      </p>
                    </div>
                    <button
                      onClick={() => setIsLetterUnfolded(true)}
                      className="px-6 py-3 rounded-xl bg-purple-400 text-black font-mono text-xs font-bold uppercase tracking-wider hover:bg-white transition-all shadow-lg"
                    >
                      SEE MESSAGE
                    </button>
                  </div>
                ) : (
                  <div className="space-y-6 animate-fadeIn">
                    
                    <div className="border-l-2 border-purple-400/50 pl-6 space-y-4 text-neutral-200 text-sm sm:text-base leading-relaxed font-serif">
                      <p className="font-bold text-white font-mono text-xs uppercase tracking-widest text-purple-300 mb-2">
                        TO MY PROFESSOR:
                      </p>
                      <p>
                        Thank you so much for such an inspiring, mind-expanding semester in Social Psychology! Exploring Chapter 2 and diving deep into the ways our self-concept, reflected appraisals, and loci of control are continuously shaped by our environment has been one of the highlights of my academic journey.
                      </p>
                      <p>
                        This workspace project was built with so much gratitude for your inspiring lectures, thoughtful feedback, and dedication to pushing us to think deeply about human social architecture.
                      </p>
                      <p>
                        I hope you enjoy exploring this digital canvas!
                      </p>
                      <p className="pt-2 text-white italic">
                        See you soon!
                      </p>
                    </div>

                    <div className="pt-4 border-t border-white/10 flex justify-between items-center font-mono text-xs">
                      <span className="text-purple-300 font-bold">Warmest regards,</span>
                      <span className="text-white text-base font-serif font-bold italic">Anna</span>
                    </div>

                    <div className="text-center pt-2">
                      <button
                        onClick={() => setIsLetterModalOpen(false)}
                        className="px-6 py-2.5 rounded-xl bg-neutral-900 border border-white/10 text-neutral-300 hover:text-white font-mono text-xs"
                      >
                        CLOSE LETTER
                      </button>
                    </div>

                  </div>
                )}

              </div>

            </div>
          </div>
        )}

        {/* Footer info bar */}
        <footer className="mt-auto py-4 text-center text-xs text-neutral-600 font-mono border-t border-white/5">
          GNED-135 MOVIE ANALYSIS // ANNA SHAHED // INCEPTION (2010) CASE STUDY
        </footer>

      </div>
    </div>
  );
}