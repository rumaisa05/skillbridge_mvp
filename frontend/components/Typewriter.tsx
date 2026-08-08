"use client";

import { useEffect, useMemo, useState } from "react";

interface TypeSegment {
  text: string;
  className?: string;
}

interface TypewriterProps {
  text: string | TypeSegment[];
  speed?: number;
  startDelay?: number;
  className?: string;
  cursorClassName?: string;
  onComplete?: () => void;
}

function getSegments(text: string | TypeSegment[]): TypeSegment[] {
  if (typeof text === "string") {
    return [{ text, className: undefined }];
  }
  return text;
}

export default function Typewriter({
  text,
  speed = 60,
  startDelay = 500,
  className = "",
  cursorClassName = "",
  onComplete,
}: TypewriterProps) {
  const segments = useMemo(() => getSegments(text), [text]);
  const totalChars = useMemo(
    () => segments.reduce((sum, segment) => sum + segment.text.length, 0),
    [segments]
  );
  const [charIndex, setCharIndex] = useState(0);
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    setCharIndex(0);
    setIsTyping(false);

    if (startDelay <= 0) {
      setIsTyping(true);
      return;
    }

    const startDelayTimeout = setTimeout(() => setIsTyping(true), startDelay);
    return () => clearTimeout(startDelayTimeout);
  }, [text, startDelay]);

  useEffect(() => {
    if (!isTyping) {
      return;
    }

    if (charIndex >= totalChars) {
      setIsTyping(false);
      onComplete?.();
      return;
    }

    const timeout = setTimeout(() => {
      setCharIndex((current) => current + 1);
    }, speed);

    return () => clearTimeout(timeout);
  }, [charIndex, isTyping, speed, totalChars, onComplete]);

  let remaining = charIndex;
  const renderedSegments = segments.map((segment, index) => {
    const visible = Math.min(remaining, segment.text.length);
    remaining = Math.max(0, remaining - segment.text.length);

    return (
      <span key={`${segment.text}-${index}`} className={segment.className}>
        {segment.text.slice(0, visible)}
      </span>
    );
  });

  return (
    <span className={className}>
      {renderedSegments}
      <span
        className={`inline-block w-[0.08em] h-[0.9em] ml-1 align-middle bg-current ${isTyping ? "animate-pulse" : ""} ${cursorClassName}`}
        style={{ animation: isTyping ? "blink-caret 0.8s step-end infinite" : "none" }}
      />
    </span>
  );
}
