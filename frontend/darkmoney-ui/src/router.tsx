import { createBrowserRouter } from "react-router-dom";
import MainLayout from "./layouts/MainLayout";

import Home from "./pages/Home";
import Donors from "./pages/Donors";
import DonorDetail from "./pages/DonorDetail";
import Recipients from "./pages/Recipients";
import RecipientDetail from "./pages/RecipientDetail";
import Topics from "./pages/Topics";
import TopicDetail from "./pages/TopicDetail";
import StatePage from "./pages/State";
import Proposition from "./pages/Proposition";
import Election from "./pages/Election";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { index: true, element: <Home /> },

      { path: "donors", element: <Donors /> },
      { path: "donors/:donorName", element: <DonorDetail /> },

      { path: "recipients", element: <Recipients /> },
      { path: "recipients/:recipientName", element: <RecipientDetail /> },

      { path: "topics", element: <Topics /> },
      { path: "topics/:ideology", element: <TopicDetail /> },

      { path: "state/:level/:stateName", element: <StatePage /> },
      { path: "propositions/:level/:billId", element: <Proposition /> },
      { path: "elections/:level/:electionId", element: <Election /> },
    ],
  },
]);
