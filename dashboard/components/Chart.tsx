import { Line } from "react-chartjs-2";
import { Chart as ChartJS, LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend } from "chart.js";
ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend);

export default function ChartMini({ data }: { data: number[] }) {
  return <Line data={{
    labels: data.map((_, i) => `t${i}`),
    datasets: [{ label: "Requests", data }]
  }} options={{ responsive: true, maintainAspectRatio: false }} />;
}
