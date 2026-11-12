import React from "react";
import { Composition } from "remotion";
import { Video, TOTAL } from "./Video";

// Duas versões: Instagram/TikTok ("link da bio") e Telegram/Facebook ("link aqui embaixo").
export const Root: React.FC = () => (
  <>
    <Composition id="VideoFixado" component={Video} durationInFrames={TOTAL} fps={30} width={1080} height={1920} defaultProps={{ versao: "instagram" as const }} />
    <Composition id="VideoFixadoOutras" component={Video} durationInFrames={TOTAL} fps={30} width={1080} height={1920} defaultProps={{ versao: "outras" as const }} />
  </>
);
