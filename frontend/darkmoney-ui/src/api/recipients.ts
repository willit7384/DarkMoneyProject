import api from "./client";
import type { Recipient } from "../types/recipient";

export async function fetchTopRecipients(): Promise<Recipient[]> {
  const res = await api.get<Recipient[]>("/recipients");
  return res.data;
}
