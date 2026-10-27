import { useState, useEffect } from "react";
import { 
  Trophy, Flame, Zap, Award, Compass, ShieldCheck, 
  Layers, GitBranch, Share2, Sparkles, Star, Users, Medal
} from "lucide-react";
import GlassCard from "../../components/ui/GlassCard.jsx";
import api from "../../lib/api.js";

const BADGE_ICONS = {
  compass: Compass,
  "shield-check": ShieldCheck,
  flame: Flame,
  layers: Layers,
  "git-branch": GitBranch,
  "share-2": Share2,
  sparkles: Sparkles,
  award: Award,
};

const ALL_POSSIBLE_BADGES = [
  { name: "Diagnostic Pioneer", desc: "Completed your first comprehensive diagnostic assessment.", icon: "compass" },
  { name: "Streak Master", desc: "Maintained an active continuous study streak of 5+ days.", icon: "flame" },
  { name: "Array Ace", desc: "Achieved Strong mastery (≥ 80%) on Arrays and Memory Layouts.", icon: "layers" },
  { name: "Tree Titan", desc: "Achieved Strong mastery (≥ 80%) on Tree Traversals and BST.", icon: "git-branch" },
  { name: "Graph Gladiator", desc: "Achieved Strong mastery (≥ 80%) on Graph BFS/DFS Algorithms.", icon: "share-2" },
  { name: "Mastery Gatekeeper", desc: "Passed a Stage 3 Mastery Gate with score ≥ 80%.", icon: "shield-check" },
  { name: "Adaptive Explorer", desc: "Engaged with personalized daily learning activities and AI tutor.", icon: "sparkles" },
];

export default function Achievements() {
  const [stats, setStats] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get("/gamification/stats"),
      api.get("/gamification/leaderboard")
    ])
      .then(([statsRes, leadRes]) => {
        setStats(statsRes.data);
        setLeaderboard(leadRes.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const earnedBadgeNames = new Set(stats?.badges?.map((b) => b.badge_name) || []);

  return (
    <div className="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-brand-gradient">
          Gamification & Mastery Achievements
        </h1>
        <p className="text-slate-400 text-xs mt-0.5">
          Competency milestone badges, active study streak progression, and cohort leaderboard.
        </p>
      </div>

      {/* Progress & Tier Rank Overview */}
      <div className="grid md:grid-cols-3 gap-4">
        {/* Tier Card */}
        <GlassCard className="flex flex-col justify-between p-5 border-brand-500/30">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-1">
              Current Competency Rank
            </span>
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-brand-gradient shadow-lg shadow-brand-500/25">
                <Trophy size={24} className="text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">
                  {stats?.rank || "Gold Strategist"}
                </h3>
                <span className="text-xs text-brand-300 font-semibold">
                  {stats?.xp_points || 1240} Total XP
                </span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-white/10">
            <div className="flex justify-between text-xs text-slate-400 mb-1.5">
              <span>Next Rank Progress</span>
              <span>{stats?.progress_pct || 62}%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-white/5 overflow-hidden">
              <div
                className="h-full bg-brand-gradient transition-all duration-500"
                style={{ width: `${stats?.progress_pct || 62}%` }}
              />
            </div>
            <span className="text-[10px] text-slate-500 block text-right mt-1">
              Next Tier at {stats?.next_rank_xp || 2000} XP
            </span>
          </div>
        </GlassCard>

        {/* Streak Card */}
        <GlassCard className="flex flex-col justify-between p-5 border-orange-500/30">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-1">
              Study Streak Telemetry
            </span>
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-orange-500/20 text-orange-400">
                <Flame size={24} className="fill-orange-400" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">
                  {stats?.current_streak || 5} Days
                </h3>
                <span className="text-xs text-orange-400 font-medium">
                  Longest: {stats?.longest_streak || 12} days
                </span>
              </div>
            </div>
          </div>

          <p className="text-slate-400 text-xs mt-3 leading-relaxed">
            Practice daily or complete a learning path task to maintain your multiplier!
          </p>
        </GlassCard>

        {/* Badges Count Card */}
        <GlassCard className="flex flex-col justify-between p-5 border-accent-500/30">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-1">
              Milestone Badges Earned
            </span>
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-accent-500/20 text-accent-400">
                <Award size={24} />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">
                  {stats?.badges?.length || 4} of {ALL_POSSIBLE_BADGES.length}
                </h3>
                <span className="text-xs text-accent-300 font-medium">
                  Competency Verified
                </span>
              </div>
            </div>
          </div>

          <p className="text-slate-400 text-xs mt-3 leading-relaxed">
            Unlock new badges by passing Stage 3 Mastery Gates with score ≥ 80%.
          </p>
        </GlassCard>
      </div>

      {/* Badges Grid Showcase */}
      <div>
        <h2 className="text-base font-semibold text-white mb-3 flex items-center gap-2">
          <Award size={18} className="text-brand-400" />
          Competency & Skill Badges
        </h2>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {ALL_POSSIBLE_BADGES.map((b) => {
            const isEarned = earnedBadgeNames.has(b.name);
            const IconComponent = BADGE_ICONS[b.icon] || Award;
            return (
              <GlassCard
                key={b.name}
                className={`p-4 border transition flex flex-col justify-between ${
                  isEarned
                    ? "border-brand-500/40 bg-brand-500/10 shadow-lg shadow-brand-500/10"
                    : "border-white/5 bg-white/[0.02] opacity-40 grayscale"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className={`p-2 rounded-xl ${isEarned ? "bg-brand-500/20 text-brand-300" : "bg-white/5 text-slate-500"}`}>
                      <IconComponent size={20} />
                    </div>
                    {isEarned ? (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-bold uppercase">
                        Unlocked
                      </span>
                    ) : (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/5 text-slate-500 uppercase">
                        Locked
                      </span>
                    )}
                  </div>

                  <h4 className="text-sm font-bold text-white">{b.name}</h4>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                    {b.desc}
                  </p>
                </div>

                <div className="mt-4 pt-2 border-t border-white/5 text-[10px] text-slate-500">
                  {isEarned ? "Verified in curriculum" : "Requirement unfulfilled"}
                </div>
              </GlassCard>
            );
          })}
        </div>
      </div>

      {/* Cohort Leaderboard */}
      <GlassCard className="p-5 border-white/10">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Users size={18} className="text-brand-400" />
            <h2 className="text-sm font-semibold text-white">Department Cohort Leaderboard</h2>
          </div>
          <span className="text-xs text-slate-400">Computer Science & Engineering</span>
        </div>

        <div className="space-y-2 text-xs">
          {leaderboard.map((st) => (
            <div
              key={st.reg_number}
              className={`p-3 rounded-xl border flex items-center justify-between transition ${
                st.reg_number === "CS2026-0042"
                  ? "bg-brand-500/20 border-brand-500/40 font-semibold text-white"
                  : "bg-white/[0.02] border-white/5 text-slate-300 hover:bg-white/5"
              }`}
            >
              <div className="flex items-center gap-3">
                <span className={`w-6 text-center font-bold text-sm ${
                  st.rank === 1 ? "text-amber-400" : st.rank === 2 ? "text-slate-300" : st.rank === 3 ? "text-amber-600" : "text-slate-500"
                }`}>
                  #{st.rank}
                </span>
                <div>
                  <p className="text-slate-100">{st.reg_number}</p>
                  <p className="text-slate-500 text-[10px]">{st.department}</p>
                </div>
              </div>

              <div className="flex items-center gap-5">
                <span className="flex items-center gap-1 text-orange-400">
                  <Flame size={13} className="fill-orange-400" />
                  {st.streak}d
                </span>
                <span className="flex items-center gap-1 text-accent-300">
                  <Award size={13} />
                  {st.badges_count} badges
                </span>
                <span className="font-bold text-brand-300 w-20 text-right">
                  {st.xp_points} XP
                </span>
              </div>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
}
