import React from "react";
import { Route, Routes } from "react-router-dom";
import LobbyPage from "@/ui/pages/LobbyPage";
import LoginPage from "@/ui/pages/LoginPage";
import ProfilePage from "@/ui/pages/ProfilePage";
import TablePage from "@/ui/pages/TablePage";
import { AuthProvider } from "@/ui/auth/AuthContext";
import { ToastProvider } from "@/ui/toasts/ToastContext";
import AppLayout from "@/ui/layout/AppLayout";
import RequireAuth from "@/ui/layout/RequireAuth";

export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <AppLayout>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<LobbyPage />} />
            <Route
              path="/tables/:tableId"
              element={
                <RequireAuth>
                  <TablePage />
                </RequireAuth>
              }
            />
            <Route
              path="/profile"
              element={
                <RequireAuth>
                  <ProfilePage />
                </RequireAuth>
              }
            />
            <Route path="*" element={<LobbyPage />} />
          </Routes>
        </AppLayout>
      </AuthProvider>
    </ToastProvider>
  );
}
