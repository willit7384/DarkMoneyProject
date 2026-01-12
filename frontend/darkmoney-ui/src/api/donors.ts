import api from "./client";
import type { Donor } from "../types/donor";

export async function fetchTopDonors(): Promise<Donor[]> {
  const res = await api.get<Donor[]>("/grants");
  return res.data;
}
