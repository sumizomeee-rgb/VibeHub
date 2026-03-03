import { useEffect, useRef, useState } from 'react';
import p5 from 'p5';

export default function P5Background() {
  const containerRef = useRef();
  const [theme, setTheme] = useState(document.documentElement.dataset.theme || 'light');

  // Listen for theme changes on the html tag
  useEffect(() => {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'data-theme') {
          setTheme(document.documentElement.dataset.theme);
        }
      });
    });
    observer.observe(document.documentElement, { attributes: true });
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const sketch = (p) => {
      let particles = [];
      let noiseZ = 0;
      let seed = Math.floor(Math.random() * 10000);
      
      const CONFIG = {
        particleCount: 600, // Reduced slightly for cleaner look
        noiseScale: 0.003,
        baseSpeed: 0.5,
        maxSpeed: 2.5,
        connectionDistance: 90, // Increased connection distance for more structure
        mouseInfluenceRadius: 200,
        mouseInfluenceStrength: 0.08
      };

      class Particle {
        constructor() {
          this.pos = p.createVector(p.random(p.width), p.random(p.height));
          this.vel = p.createVector(0, 0);
          this.acc = p.createVector(0, 0);
          this.maxSpeed = p.random(CONFIG.baseSpeed, CONFIG.maxSpeed) * 0.8;
          
          this.size = p.random(1.5, 3.5);
          
          // Store base characteristics to calculate theme-dependent colors during render
          this.colorType = p.random([0, 1, 2, 3]); // 4 color types
        }

        update() {
          this.vel.add(this.acc);
          this.vel.limit(this.maxSpeed);
          this.pos.add(this.vel);
          this.acc.mult(0);

          // Wrap edges smoothly
          if (this.pos.x > p.width + 50) this.pos.x = -50;
          if (this.pos.x < -50) this.pos.x = p.width + 50;
          if (this.pos.y > p.height + 50) this.pos.y = -50;
          if (this.pos.y < -50) this.pos.y = p.height + 50;
        }

        applyForce(force) {
          this.acc.add(force);
        }

        follow(flowField, cols) {
          let x = p.floor(this.pos.x / 20);
          let y = p.floor(this.pos.y / 20);
          // Boundary check
          if (x >= 0 && x < cols && y >= 0 && y < flowField.length / cols) {
            let index = x + y * cols;
            if (flowField[index]) {
              let force = flowField[index].copy();
              this.applyForce(force);
            }
          }
        }

        reactToMouse(mx, my) {
          let mousePos = p.createVector(mx, my);
          let d = p.dist(this.pos.x, this.pos.y, mousePos.x, mousePos.y);
          if (d < CONFIG.mouseInfluenceRadius) {
            let repelForce = p5.Vector.sub(this.pos, mousePos);
            repelForce.setMag(p.map(d, 0, CONFIG.mouseInfluenceRadius, CONFIG.mouseInfluenceStrength, 0));
            this.applyForce(repelForce);
          }
        }

        show(isDark) {
          p.noStroke();
          
          // Theme-aware coloring
          let c;
          let alpha = isDark ? 90 : 120; // Brighter particles in light mode
          
          if (this.colorType === 0) c = isDark ? p.color(129, 140, 248, alpha) : p.color(79, 70, 229, alpha); // Primary
          else if (this.colorType === 1) c = isDark ? p.color(96, 165, 250, alpha) : p.color(14, 165, 233, alpha); // Cyan/Info
          else if (this.colorType === 2) c = isDark ? p.color(52, 211, 153, alpha) : p.color(16, 185, 129, alpha); // Emerald
          else c = isDark ? p.color(255, 255, 255, alpha * 0.8) : p.color(100, 116, 139, alpha * 0.6); // Neutral 
          
          p.fill(c);
          p.circle(this.pos.x, this.pos.y, this.size);
        }
      }

      p.setup = () => {
        p.createCanvas(p.windowWidth, p.windowHeight);
        p.noiseSeed(seed);
        
        for (let i = 0; i < CONFIG.particleCount; i++) {
          particles.push(new Particle());
        }
      };

      p.draw = () => {
        const isDark = document.documentElement.dataset.theme === 'dark';
        
        // Clear background completely every frame for true transparency over CSS background
        p.clear();

        // Calculate flow field
        let cols = p.floor(p.width / 20) + 1;
        let rows = p.floor(p.height / 20) + 1;
        let flowField = new Array(cols * rows);

        let yoff = 0;
        for (let y = 0; y < rows; y++) {
          let xoff = 0;
          for (let x = 0; x < cols; x++) {
            let index = x + y * cols;
            let angle = p.noise(xoff, yoff, noiseZ) * p.TWO_PI * 4;
            let v = p.constructor.Vector.fromAngle(angle);
            v.setMag(0.3); // Softer flow
            flowField[index] = v;
            xoff += CONFIG.noiseScale;
          }
          yoff += CONFIG.noiseScale;
        }

        noiseZ += 0.001;

        // Draw connections
        p.strokeWeight(1);
        for (let i = 0; i < particles.length; i++) {
          let p1 = particles[i];
          
          // Optimization: Only check a subset of particles for connections based on index
          // This creates a more web-like, structured feel rather than a messy hairball
          let connectionCount = 0;
          for (let j = i + 1; j < particles.length; j += (i % 3 === 0 ? 1 : 2)) {
            if (connectionCount > 4) break; // Max 4 connections per particle to keep it clean
            
            let p2 = particles[j];

            // Quick distance check before expensive p.dist()
            if (Math.abs(p1.pos.x - p2.pos.x) < CONFIG.connectionDistance && 
                Math.abs(p1.pos.y - p2.pos.y) < CONFIG.connectionDistance) {
                
              let d = p.dist(p1.pos.x, p1.pos.y, p2.pos.x, p2.pos.y);
              
              if (d < CONFIG.connectionDistance) {
                connectionCount++;
                
                // Opacity based on distance
                let maxAlpha = isDark ? 80 : 100;
                let alpha = p.map(d, 0, CONFIG.connectionDistance, maxAlpha, 0);
                
                // Color lines based on theme. Dark mode = light lines, Light mode = dark lines
                let lineCol = isDark ? p.color(165, 180, 252, alpha) : p.color(99, 102, 241, alpha);
                p.stroke(lineCol);
                p.line(p1.pos.x, p1.pos.y, p2.pos.x, p2.pos.y);
              }
            }
          }
        }

        // Update and Display Particles
        for (let particle of particles) {
          particle.follow(flowField, cols);
          if (p.mouseX !== 0 && p.mouseY !== 0) {
            particle.reactToMouse(p.mouseX, p.mouseY);
          }
          particle.update();
          particle.show(isDark);
        }
      };

      p.windowResized = () => {
        p.resizeCanvas(p.windowWidth, p.windowHeight);
      };
    };

    const p5Instance = new p5(sketch, containerRef.current);

    return () => {
      p5Instance.remove();
    };
  }, [theme]); // Re-initialize if theme dramatically shifts (fallback)

  return (
    <div 
      ref={containerRef} 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: -1,
        pointerEvents: 'none', 
        opacity: 0.8, // Slightly fade the whole canvas back
      }}
    />
  );
}
