import useSWR from "swr";
import axios from "axios";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const fetcher = (url: string) => axios.get(url).then(r => r.data);

export default function RepoStatus() {
  const GW = process.env.NEXT_PUBLIC_GATEWAY_URL || process.env.GATEWAY_URL || "http://localhost:3000";
  const { data, error, isLoading } = useSWR(`${GW}/v1/repo/status`, fetcher, { refreshInterval: 10000 });

  // نحضر بيانات رسومية بسيطة: commits و PRs
  const commitsCount = data?.commits_last_week?.length || 0;
  const prsCount = data?.open_prs?.length || 0;
  const branchesCount = data?.branches?.length || 0;

  const chartData = {
    labels: ["Commits (7d)", "Open PRs", "Branches"],
    datasets: [
      {
        label: "Repository Stats",
        data: [commitsCount, prsCount, branchesCount],
        backgroundColor: ["#3b82f6", "#10b981", "#f59e0b"]
      }
    ]
  };

  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="p-6 space-y-6">
          <h1 className="text-xl font-semibold">📦 Repository Status</h1>

          {isLoading && <p>Loading status...</p>}
          {error && <p className="text-red-600">Error: {error.message}</p>}

          {data && (
            <>
              <div className="bg-white border rounded p-4 space-y-2">
                <h2 className="font-semibold">Latest Commit</h2>
                <p><span className="font-medium">SHA:</span> {data.latest_commit.sha}</p>
                <p><span className="font-medium">Message:</span> {data.latest_commit.message}</p>
                <p><span className="font-medium">Author:</span> {data.latest_commit.author?.name}</p>
              </div>

              <div className="bg-white border rounded p-4 space-y-2">
                <h2 className="font-semibold">Repository Stats</h2>
                <div className="h-64">
                  <Bar data={chartData} options={{ responsive: true, maintainAspectRatio: false }} />
                </div>
              </div>

              <div className="bg-white border rounded p-4 space-y-2">
                <h2 className="font-semibold">Branches</h2>
                <ul className="list-disc pl-6">
                  {data.branches.map((b: string) => (
                    <li key={b}>{b}</li>
                  ))}
                </ul>
              </div>

              <div className="bg-white border rounded p-4 space-y-2">
                <h2 className="font-semibold">Open Pull Requests</h2>
                {data.open_prs.length === 0 ? (
                  <p>No open PRs 🚀</p>
                ) : (
                  <ul className="list-disc pl-6">
                    {data.open_prs.map((pr: any) => (
                      <li key={pr.number}>
                        #{pr.number} — {pr.title} <span className="text-sm text-gray-500">by {pr.user}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
