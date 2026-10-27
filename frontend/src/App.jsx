import { Navigate, Route, Routes } from "react-router-dom";
import AdminDashboard from "./pages/admin/AdminDashboard.jsx";
import Login from "./pages/Login.jsx";
import CompetencyReport from "./pages/student/CompetencyReport.jsx";
import StudentDashboard from "./pages/student/Dashboard.jsx";
import DiagnosticQuiz from "./pages/student/DiagnosticQuiz.jsx";
import AdaptivePractice from "./pages/student/AdaptivePractice.jsx";
import AITutor from "./pages/student/AITutor.jsx";
import LearningPath from "./pages/student/LearningPath.jsx";
import StudyHub from "./pages/student/StudyHub.jsx";
import Achievements from "./pages/student/Achievements.jsx";
import CareerStageAssessment from "./pages/student/CareerStageAssessment.jsx";
import TeacherDashboard from "./pages/teacher/TeacherDashboard.jsx";
import Navbar from "./components/layout/Navbar.jsx";
import { useAuthStore } from "./store/authStore.js";

function ProtectedRoute({ role, children }) {
  const { token, role: currentRole } = useAuthStore();
  if (!token) return <Navigate to="/login" replace />;
  if (role && currentRole !== role) return <Navigate to={`/${currentRole || "login"}`} replace />;

  return (
    <div className="min-h-screen flex flex-col bg-[#0b0f19] text-slate-100">
      <Navbar />
      <main className="flex-1 pb-10">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />

      {/* Student Protected Routes */}
      <Route
        path="/student"
        element={
          <ProtectedRoute role="student">
            <StudentDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/career-stage"
        element={
          <ProtectedRoute role="student">
            <CareerStageAssessment />
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/learning-path"
        element={
          <ProtectedRoute role="student">
            <LearningPath />
          </ProtectedRoute>
        }
      />

      <Route
        path="/student/practice"
        element={
          <ProtectedRoute role="student">
            <AdaptivePractice />
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/tutor"
        element={
          <ProtectedRoute role="student">
            <AITutor />
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/materials"
        element={
          <ProtectedRoute role="student">
            <StudyHub />
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/achievements"
        element={
          <ProtectedRoute role="student">
            <Achievements />
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/course/:courseId/diagnostic"
        element={
          <ProtectedRoute role="student">
            <DiagnosticQuiz />
          </ProtectedRoute>
        }
      />
      <Route
        path="/student/course/:courseId/report"
        element={
          <ProtectedRoute role="student">
            <CompetencyReport />
          </ProtectedRoute>
        }
      />

      {/* Faculty & Administration Routes */}
      <Route
        path="/teacher"
        element={
          <ProtectedRoute role="teacher">
            <TeacherDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <ProtectedRoute role="admin">
            <AdminDashboard />
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
