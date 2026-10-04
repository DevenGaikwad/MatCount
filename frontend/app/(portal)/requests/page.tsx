import type { Metadata } from "next";
import { RequestsView } from "@/features/requests/requests-view";
export const metadata: Metadata = { title: "Component Requests" };
export default function RequestsPage() { return <RequestsView />; }
