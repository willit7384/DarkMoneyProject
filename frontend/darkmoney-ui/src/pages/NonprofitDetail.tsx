import { useParams } from "react-router-dom";

export default function NonprofitDetail() {
  const { donorName: nonprofitName } = useParams();
  return <h2>Nonprofit: {nonprofitName}</h2>;
}
