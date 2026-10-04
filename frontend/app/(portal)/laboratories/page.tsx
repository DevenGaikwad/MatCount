import type { Metadata } from "next";
import { LaboratoriesView } from "@/features/master-data/laboratories-view";
export const metadata: Metadata = { title: "Laboratories" };
export default function LaboratoriesPage() { return <LaboratoriesView />; }
