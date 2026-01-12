import { useParams } from "react-router-dom";

export default function DonorDetail() {
  const { donorName } = useParams();
  return <h2>Donor: {donorName}</h2>;
}
