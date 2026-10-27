import { useState, useEffect, useRef } from "react";
import { 
  Bot, Send, Sparkles, ShieldCheck, BookOpen, Globe, RefreshCw, 
  CheckCircle, AlertCircle, Lightbulb, User, ArrowRight
} from "lucide-react";
import GlassCard from "../../components/ui/GlassCard.jsx";
import api from "../../lib/api.js";

export default function AITutor() {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState("");
  const [language, setLanguage] = useState("english");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [suggestedPrompts, setSuggestedPrompts] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Fetch courses
    api.get("/courses").then((res) => {
      setCourses(res.data);
      if (res.data.length > 0) setSelectedCourse(res.data[0].id);
    }).catch(() => {});

    // Fetch suggested prompts
    api.get("/tutor/suggested-prompts").then((res) => {
      setSuggestedPrompts(res.data);
    }).catch(() => {});

    // Fetch previous chat history
    api.get("/tutor/history").then((res) => {
      if (res.data && res.data.length > 0) {
        const formatted = res.data.map((h) => ([
          { sender: "user", text: h.message, timestamp: h.created_at },
          { sender: "ai", text: h.response, sources: h.source_refs, timestamp: h.created_at }
        ])).flat();
        setMessages(formatted);
      } else {
        setMessages([
          {
            sender: "ai",
            text: "Hello! I am your **SkillPath AI Grounded Tutor**.\n\nI answer your questions strictly using your verified course curriculum materials with zero hallucinations. Ask me to break down any algorithm, data structure, or concept from your enrolled syllabus!",
            sources: ["Verified Course Notes", "SkillPath Curriculum Repository"],
            grounded: true,
            confidence: 0.98,
          }
        ]);
      }
    }).catch(() => {
      setMessages([
        {
          sender: "ai",
          text: "Hello! I am your **SkillPath AI Grounded Tutor**.\n\nAsk me any concept or challenge from your course syllabus!",
          sources: ["Verified Course Notes"],
          grounded: true,
        }
      ]);
    });
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend(textToSend) {
    const query = textToSend || input;
    if (!query.trim() || loading) return;

    const userMsg = { sender: "user", text: query, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const { data } = await api.post("/tutor/chat", {
        message: query,
        course_id: selectedCourse,
        language: language,
      });

      const aiMsg = {
        sender: "ai",
        text: data.response,
        sources: data.sources || [],
        confidence: data.confidence || 0.90,
        grounded: data.grounded,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text: "⚠️ Unable to connect to AI retrieval engine. Please ensure backend server is active.",
          sources: [],
          grounded: false,
        }
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-brand-gradient">
              RAG AI Pedagogical Tutor
            </h1>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-semibold">
              <ShieldCheck size={13} /> Grounded in Syllabus
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Zero-hallucination semantic retrieval powered by Sentence-Transformers vector embeddings and course textbooks.
          </p>
        </div>

        {/* Course & Language Selectors */}
        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs">
            <BookOpen size={14} className="text-brand-400" />
            <select
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none text-xs"
            >
              {courses.map((c) => (
                <option key={c.id} value={c.id} className="bg-slate-900 text-white">
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs">
            <Globe size={14} className="text-accent-400" />
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none text-xs capitalize"
            >
              <option value="english" className="bg-slate-900 text-white">English</option>
              <option value="hindi" className="bg-slate-900 text-white">Hindi (हिन्दी)</option>
              <option value="hinglish" className="bg-slate-900 text-white">Hinglish</option>
            </select>
          </div>
        </div>
      </div>

      {/* Suggested Prompts Pill Carousel */}
      {suggestedPrompts.length > 0 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          <span className="text-slate-400 text-[11px] font-semibold uppercase tracking-wider flex items-center gap-1 shrink-0">
            <Lightbulb size={13} className="text-amber-400" />
            Suggested:
          </span>
          {suggestedPrompts.slice(0, 4).map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(p)}
              disabled={loading}
              className="px-3 py-1.5 rounded-xl bg-white/5 hover:bg-brand-500/20 hover:text-white border border-white/5 hover:border-brand-500/30 text-slate-300 text-xs whitespace-nowrap transition"
            >
              {p}
            </button>
          ))}
        </div>
      )}

      {/* Chat Messages Area */}
      <GlassCard className="flex flex-col h-[560px] p-4 sm:p-6 border-white/10 relative">
        <div className="flex-1 overflow-y-auto space-y-4 pr-2">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex gap-3 ${
                m.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {m.sender === "ai" && (
                <div className="w-8 h-8 rounded-xl bg-brand-gradient flex items-center justify-center shrink-0 shadow-md">
                  <Bot size={16} className="text-white" />
                </div>
              )}

              <div
                className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 text-xs sm:text-sm leading-relaxed ${
                  m.sender === "user"
                    ? "bg-brand-600 text-white rounded-br-none shadow-lg shadow-brand-600/20"
                    : "bg-white/[0.04] border border-white/10 text-slate-200 rounded-bl-none"
                }`}
              >
                <div className="whitespace-pre-line prose-invert">
                  {m.text}
                </div>

                {/* Sources & Citations if AI */}
                {m.sender === "ai" && m.sources && m.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-white/10 text-[11px] text-slate-400">
                    <p className="font-semibold text-slate-300 mb-1 flex items-center gap-1">
                      <ShieldCheck size={12} className="text-emerald-400" />
                      Grounded Course Sources ({Math.round((m.confidence || 0.9) * 100)}% match):
                    </p>
                    <div className="flex flex-wrap gap-1.5 mt-1">
                      {m.sources.map((src, sIdx) => (
                        <span
                          key={sIdx}
                          className="px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-brand-300 text-[10px]"
                        >
                          {src}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {m.sender === "user" && (
                <div className="w-8 h-8 rounded-xl bg-white/10 flex items-center justify-center shrink-0 border border-white/10">
                  <User size={16} className="text-slate-300" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-3 items-center text-xs text-slate-400">
              <div className="w-8 h-8 rounded-xl bg-brand-gradient flex items-center justify-center shrink-0 animate-pulse">
                <Bot size={16} className="text-white" />
              </div>
              <div className="px-4 py-3 rounded-2xl bg-white/5 border border-white/10 flex items-center gap-2">
                <RefreshCw size={14} className="animate-spin text-brand-400" />
                <span>Searching vector index & grounding response in curriculum materials…</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="mt-4 pt-3 border-t border-white/10 flex items-center gap-2"
        >
          <input
            type="text"
            placeholder="Ask about data structures, time complexities, invariants..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            className="input-field text-xs sm:text-sm py-3"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="btn-primary py-3 px-4 flex items-center justify-center shrink-0 disabled:opacity-40"
          >
            <Send size={16} />
          </button>
        </form>
      </GlassCard>
    </div>
  );
}
