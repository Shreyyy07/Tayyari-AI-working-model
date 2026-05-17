"use client";

import { useEffect, useState, MouseEvent, MouseEventHandler } from "react";
import {
  useRive,
  useStateMachineInput,
  Layout,
  Fit,
  Alignment,
} from "@rive-app/react-canvas";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import useMediaQuery from "@/app/utils/useMediaBreakpoint";
import usePrefersReducedMotion from "@/app/utils/usePrefersReducedMotion";
import { throttle } from "@/app/utils/throttle";
import RocketLaunchButton from "./RocketLaunchButton";


export default function RiveHero() {
  const [lastWidth, setLastWidth] = useState(0);
  const [lastHeight, setLastHeight] = useState(0);
  const lgQuery = useMediaQuery("only screen and (min-width: 1025px)");
  const prefersReducedMotion = usePrefersReducedMotion();

  const {
    rive,
    setCanvasRef,
    setContainerRef,
    canvas: canvasRef,
    container: canvasContainerRef,
  } = useRive(
    {
      src: "/hero_use_case.riv",
      artboard: "Hero Demo Listeners Resize",
      stateMachines: "State Machine 1",
      layout: new Layout({
        fit: Fit.Cover,
        alignment: Alignment.Center,
      }),
      autoplay: true,
    },
    { shouldResizeCanvasToContainer: false }
  );

  useEffect(() => {
    if (rive) {
      rive.layout = new Layout({
        fit: Fit.Cover,
        alignment: Alignment.Center,
      });
    }
  }, [rive, lgQuery]);

  const numX = useStateMachineInput(rive, "State Machine 1", "numX", 50);
  const numY = useStateMachineInput(rive, "State Machine 1", "numY", 50);
  const numSize = useStateMachineInput(rive, "State Machine 1", "numSize", 0);

  useEffect(() => {
    if (rive) {
      if (prefersReducedMotion) {
        rive.pause();
      } else {
        rive.play();
      }
    }
  }, [rive, prefersReducedMotion]);

  useEffect(() => {
    if (rive && canvasRef && canvasContainerRef) {
      const resizeObserver = new ResizeObserver(
        throttle(() => {
          const newWidth = canvasContainerRef.clientWidth;
          const newHeight = canvasContainerRef.clientHeight;

          if (newWidth <= 1200 && numSize) {
            const resizeRange = 1200 - 500;
            numSize.value = Math.min(((1200 - newWidth) / resizeRange) * 100, 100);
          } else if (numSize) {
            numSize.value = 0;
          }

          const dpr = window.devicePixelRatio || 1;
          const newCanvasWidth = newWidth * dpr;
          const newCanvasHeight = newHeight * dpr;

          if (
            canvasRef &&
            (lastWidth !== newCanvasWidth || lastHeight !== newCanvasHeight)
          ) {
            canvasRef.width = newCanvasWidth;
            canvasRef.height = newCanvasHeight;

            setLastWidth(newCanvasWidth);
            setLastHeight(newCanvasHeight);

            canvasRef.style.width = `${newWidth}px`;
            canvasRef.style.height = `${newHeight}px`;

            rive.resizeToCanvas();
            rive.startRendering();
          }
        }, 16)
      );

      resizeObserver.observe(canvasContainerRef);
      return () => resizeObserver.unobserve(canvasContainerRef);
    }
  }, [rive, canvasRef, canvasContainerRef, lastWidth, lastHeight, numSize]);

  // 🔥 FIXED: Mouse movement tracking with proper coordinate calculation
  const onMouseMove: MouseEventHandler = (e: MouseEvent) => {
    if (!numX || !numY || !canvasContainerRef) return;

    // Get the bounding rectangle of the container
    const rect = canvasContainerRef.getBoundingClientRect();
    
    // Calculate relative mouse position within the container
    const relativeX = e.clientX - rect.left;
    const relativeY = e.clientY - rect.top;

    // Convert to percentage values (0-100) for Rive inputs
    const percentX = (relativeX / rect.width) * 100;
    const percentY = 100 - (relativeY / rect.height) * 100; // Invert Y for Rive coordinate system

    // Set the values for Rive state machine
    numX.value = Math.max(0, Math.min(100, percentX));
    numY.value = Math.max(0, Math.min(100, percentY));
  };

  return (
    <div
    className="relative w-full min-h-[80vh] md:min-h-[85vh] lg:min-h-[90vh] overflow-hidden cursor-crosshair pt-20" // ← Added pt-20
    ref={setContainerRef}
    onMouseMove={onMouseMove}
    style={{ touchAction: 'none' }}
  >
      {/* Canvas for Rive animation */}
      <canvas 
        ref={setCanvasRef} 
        className="absolute w-full h-full object-cover pointer-events-none" 
      />

      {/* Content Overlay */}
     <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-6 z-10 bg-gradient-to-b from-transparent via-transparent to-black/10 pointer-events-none">
  <div className="max-w-4xl mx-auto">
    <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-white mb-6 leading-tight tracking-tight drop-shadow-lg">
      Learn anything.
      <span className="block bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-blue-400 mt-2">
        Your way.
      </span>
    </h1>
    
    <p className="text-lg md:text-xl lg:text-2xl text-gray-100 mb-10 max-w-3xl mx-auto font-medium drop-shadow-md">
      Upload your content. Let AI make it interactive. Learn at your own pace — smarter, not harder.
    </p>

    <div className="flex flex-col sm:flex-row gap-6 justify-center pointer-events-auto">
      {/* Rocket Launch Button */}
      <RocketLaunchButton />
      
      <Link href="/leaderboard">
        <Button 
          variant="outline" 
          className="border-2 border-white/40 text-black hover:bg-white/10 hover:border-white/60 px-10 py-5 text-lg md:text-xl rounded-xl transition-all backdrop-blur-sm shadow-lg"
        >
          🏆 Leaderboard
        </Button>
      </Link>
    </div>
  </div>
</div>
    </div>
  );
}
