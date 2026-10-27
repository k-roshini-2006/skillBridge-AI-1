import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import GlassCard from "../../components/ui/GlassCard.jsx";
import api from "../../lib/api.js";

export default function DiagnosticQuiz() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [assessmentId, setAssessmentId] = useState(null);
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.post(`/competency/${courseId}/diagnostic/start`).then((res) => {
      if (res.data && res.data.questions) {
        setQuestions(res.data.questions);
        setAssessmentId(res.data.assessment_id);
      } else {
        setQuestions(res.data || []);
      }
      setLoading(false);
    }).catch((err) => {
      console.error(err);
      setLoading(false);
    });
  }, [courseId]);

  function selectOption(questionId, optionKey) {
    setAnswers((prev) => ({ ...prev, [questionId]: optionKey }));
  }

  async function handleSubmit() {
    const payload = {
      assessment_id: assessmentId,
      answers: Object.entries(answers).map(([question_id, selected_option]) => ({
        question_id,
        selected_option,
      })),
    };
    const { data } = await api.post("/competency/diagnostic/submit", payload);
    navigate(`/student/course/${courseId}/report`, { state: { report: data } });
  }

  if (loading) return <div className="p-10 text-center text-slate-400">Generating your diagnostic assessment…</div>;
  if (questions.length === 0) return <div className="p-10 text-center text-slate-400">No questions available yet — seed the database first.</div>;

  const q = questions[current];

  return (
    <div className="max-w-2xl mx-auto p-6">
      <p className="text-slate-400 text-sm mb-2">
        Question {current + 1} of {questions.length}
      </p>
      <GlassCard>
        <h2 className="text-lg font-semibold mb-4">{q.question_text}</h2>
        <div className="space-y-3">
          {Object.entries(q.options).map(([key, text]) => (
            <button
              key={key}
              onClick={() => selectOption(q.id, key)}
              className={`w-full text-left px-4 py-3 rounded-xl border transition ${
                answers[q.id] === key
                  ? "border-brand-500 bg-brand-500/10"
                  : "border-white/10 bg-white/5 hover:bg-white/10"
              }`}
            >
              <span className="font-medium mr-2 uppercase">{key}.</span>
              {text}
            </button>
          ))}
        </div>

        <div className="flex justify-between mt-6">
          <button
            disabled={current === 0}
            onClick={() => setCurrent((c) => c - 1)}
            className="px-4 py-2 rounded-xl bg-white/5 disabled:opacity-30"
          >
            Back
          </button>
          {current < questions.length - 1 ? (
            <button onClick={() => setCurrent((c) => c + 1)} className="btn-primary">
              Next
            </button>
          ) : (
            <button onClick={handleSubmit} className="btn-primary">
              Submit Diagnostic
            </button>
          )}
        </div>
      </GlassCard>
    </div>
  );
}
