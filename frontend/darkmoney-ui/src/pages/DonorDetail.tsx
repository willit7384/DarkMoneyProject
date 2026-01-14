import { useParams } from "react-router-dom";

export default function DonorDetail() {
  const { donorName } = useParams();
  return (
    <div>
      <h2>Donor: {donorName}</h2>
    </div>
  );
}
