import {
    PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart,
    ResponsiveContainer
} from "recharts";

export default function SkillRadar({ data }) {
  // data: [{ topic: "Arrays", score: 92 }, ...]
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={data}>
        <PolarGrid stroke="#334155" />
        <PolarAngleAxis dataKey="topic" tick={{ fill: "#cbd5e1", fontSize: 12 }} />
        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "#64748b" }} />
        <Radar
          name="Competency"
          dataKey="score"
          stroke="#a855f7"
          fill="#a855f7"
          fillOpacity={0.4}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
