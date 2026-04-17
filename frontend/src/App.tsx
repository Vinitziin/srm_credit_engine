import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import { RouterProvider, createBrowserRouter } from "react-router-dom";
import { Layout } from "./components/Layout";
import { CedentesPage } from "./pages/CedentesPage";
import { SimulatorPage } from "./pages/SimulatorPage";
import { StatementsPage } from "./pages/StatementsPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { refetchOnWindowFocus: false, retry: 1 },
  },
});

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <SimulatorPage /> },
      { path: "statements", element: <StatementsPage /> },
      { path: "cedentes", element: <CedentesPage /> },
    ],
  },
]);

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <Toaster
        position="top-right"
        toastOptions={{
          style: { background: "#1f2937", color: "#f3f4f6" },
        }}
      />
    </QueryClientProvider>
  );
}
