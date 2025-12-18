import { createBrowserRouter } from "react-router-dom";
import { AppShell } from "../App";
import { PublicLayout } from "../layouts/PublicLayout";
import { LobbyPage } from "../pages/LobbyPage";
import { LoginPage } from "../pages/LoginPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { ProfilePage } from "../pages/ProfilePage";
import { RegisterPage } from "../pages/RegisterPage";
import { RootRedirectPage } from "../pages/RootRedirectPage";
import { TablePage } from "../pages/TablePage";
import { RequireAuth } from "./RequireAuth";

export const router = createBrowserRouter([
  { path: "/", element: <RootRedirectPage /> },
  {
    element: <PublicLayout />,
    children: [
      { path: "/login", element: <LoginPage /> },
      { path: "/register", element: <RegisterPage /> }
    ]
  },
  {
    element: (
      <RequireAuth>
        <AppShell />
      </RequireAuth>
    ),
    children: [
      { path: "/lobby", element: <LobbyPage /> },
      { path: "/tables/:tableId", element: <TablePage /> },
      { path: "/profile", element: <ProfilePage /> }
    ]
  },
  { path: "*", element: <NotFoundPage /> }
]);
