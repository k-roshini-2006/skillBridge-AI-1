import { useState, useEffect } from "react";
import { 
  BookOpen, FileText, Code, HelpCircle, Star, Sparkles, 
  Search, ExternalLink, ThumbsUp, Send, Check
} from "lucide-react";
import { Link } from "react-router-dom";
import GlassCard from "../../components/ui/GlassCard.jsx";
import api from "../../lib/api.js";

const TYPE_BADGES = {
  notes: { label: "Curriculum Notes", color: "bg-blue-500/20 text-blue-300 border-blue-500/30" },
  cheatsheet: { label: "Algorithmic Cheatsheet", color: "bg-purple-500/20 text-purple-300 border-purple-500/30" },
  interview_qs: { label: "Interview Invariants", color: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" },
  video: { label: "Visual Breakdown", color: "bg-amber-500/20 text-amber-300 border-amber-500/30" },
};

export default function StudyHub() {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState("");
  const [materials, setMaterials] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState("all");
  const [selectedType, setSelectedType] = useState("all");
  const [search, setSearch] = useState("");
  const [activeMaterial, setActiveMaterial] = useState(null);

  // Feedback widget state
  const [starRating, setStarRating] = useState(5);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  useEffect(() => {
    api.get("/courses").then((res) => {
      setCourses(res.data);
      if (res.data.length > 0) setSelectedCourse(res.data[0].id);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      api.get(`/materials/course/${selectedCourse}`)
        .then((res) => {
          setMaterials(res.data);
          if (res.data.length > 0) setActiveMaterial(res.data[0]);
        })
        .catch(() => {});
    }
  }, [selectedCourse]);

  async function handleFeedbackSubmit(materialId) {
    try {
      await api.post(`/materials/${materialId}/feedback`, {
        material_id: materialId,
        star_rating: Number(starRating),
        difficulty: 3,
        helpfulness: 5,
        comment: "Excellent reference material for revision.",
      });
      setFeedbackSubmitted(true);
      setTimeout(() => setFeedbackSubmitted(false), 3000);
    } catch {}
  }

  const filtered = materials.filter((m) => {
    const matchTopic = selectedTopic === "all" || m.topic_name.toLowerCase() === selectedTopic.toLowerCase();
    const matchType = selectedType === "all" || m.type === selectedType;
    const matchSearch = !search || m.title.toLowerCase().includes(search.toLowerCase()) || m.content?.toLowerCase().includes(search.toLowerCase());
    return matchTopic && matchType && matchSearch;
  });

  const uniqueTopics = ["all", ...new Set(materials.map((m) => m.topic_name))];

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-brand-gradient">
            Curriculum & Study Materials Hub
          </h1>
          <p className="text-slate-400 text-xs mt-0.5">
            Verified textbooks, complexity cheatsheets, and interview problem sets indexed into the RAG vector space.
          </p>
        </div>

        {courses.length > 0 && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs">
            <span className="text-slate-400">Course:</span>
            <select
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none text-xs font-semibold"
            >
              {courses.map((c) => (
                <option key={c.id} value={c.id} className="bg-slate-900 text-white">
                  {c.name}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          {uniqueTopics.map((t) => (
            <button
              key={t}
              onClick={() => setSelectedTopic(t)}
              className={`px-3 py-1.5 rounded-xl font-medium capitalize transition whitespace-nowrap ${
                selectedTopic === t
                  ? "bg-brand-500/20 text-brand-300 border border-brand-500/40"
                  : "bg-white/5 text-slate-400 hover:text-white"
              }`}
            >
              {t === "all" ? "All Topics" : t}
            </button>
          ))}
        </div>

        <div className="relative sm:w-64">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search notes, complexity..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input-field pl-9 py-2 text-xs"
          />
        </div>
      </div>

      {/* Main Material Viewer Layout */}
      <div className="grid lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Material Cards List */}
        <div className="lg:col-span-5 space-y-3">
          {filtered.map((mat) => {
            const isSelected = activeMaterial?.id === mat.id;
            const badge = TYPE_BADGES[mat.type] || { label: mat.type, color: "bg-white/10 text-slate-300" };
            return (
              <GlassCard
                key={mat.id}
                onClick={() => setActiveMaterial(mat)}
                className={`p-4 border cursor-pointer transition ${
                  isSelected
                    ? "border-brand-500 bg-brand-500/15 shadow-lg shadow-brand-500/10"
                    : "border-white/10 hover:border-brand-500/30"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300">
                    {mat.topic_name}
                  </span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badge.color}`}>
                    {badge.label}
                  </span>
                </div>
                <h3 className="text-sm font-semibold text-white">{mat.title}</h3>
                <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                  {mat.content?.slice(0, 150)}…
                </p>
                <div className="mt-3 pt-2 border-t border-white/5 flex items-center justify-between text-[10px] text-slate-500">
                  <span>Source: {mat.source || "Course Curriculum"}</span>
                  <span className="text-brand-300 font-medium">Read Notes →</span>
                </div>
              </GlassCard>
            );
          })}

          {filtered.length === 0 && (
            <p className="text-slate-500 text-xs py-8 text-center">
              No study materials matching this filter.
            </p>
          )}
        </div>

        {/* Right Column: Full Material Reader & Interactive Feedback */}
        <div className="lg:col-span-7">
          {activeMaterial ? (
            <GlassCard className="p-6 border-white/10 space-y-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-white/10">
                <div>
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300">
                      {activeMaterial.topic_name}
                    </span>
                    <span className="text-[10px] text-slate-400">
                      Indexed for RAG Vector Search
                    </span>
                  </div>
                  <h2 className="text-lg font-bold text-white">
                    {activeMaterial.title}
                  </h2>
                </div>

                <Link
                  to="/student/tutor"
                  className="px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-brand-300 hover:text-white flex items-center gap-1.5 shrink-0 transition"
                >
                  <HelpCircle size={14} />
                  <span>Ask AI Tutor</span>
                </Link>
              </div>

              {/* Reader Content Body */}
              <div className="prose prose-invert max-w-none text-xs sm:text-sm leading-relaxed text-slate-200 whitespace-pre-line font-mono bg-white/[0.02] p-5 rounded-2xl border border-white/5 max-h-[500px] overflow-y-auto">
                {activeMaterial.content}
              </div>

              {/* Material Feedback Widget */}
              <div className="pt-4 border-t border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-3">
                  <span className="text-slate-400">Rate this resource:</span>
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map((s) => (
                      <button
                        key={s}
                        onClick={() => setStarRating(s)}
                        className={`transition ${s <= starRating ? "text-amber-400" : "text-slate-600"}`}
                      >
                        <Star size={16} className={s <= starRating ? "fill-amber-400" : ""} />
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleFeedbackSubmit(activeMaterial.id)}
                    className="px-3.5 py-1.5 rounded-xl bg-brand-500/20 hover:bg-brand-500/30 text-brand-300 border border-brand-500/30 text-xs font-semibold flex items-center gap-1.5 transition"
                  >
                    <ThumbsUp size={13} />
                    <span>{feedbackSubmitted ? "Saved (+15 XP)!" : "Submit Feedback (+15 XP)"}</span>
                  </button>
                </div>
              </div>
            </GlassCard>
          ) : (
            <GlassCard className="p-12 text-center text-slate-400">
              <BookOpen size={32} className="mx-auto mb-2 text-brand-400" />
              <p>Select any material on the left to review its content.</p>
            </GlassCard>
          )}
        </div>
      </div>
    </div>
  );
}
