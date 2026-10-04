import type { Metadata } from "next";
import { ComponentsView } from "@/features/master-data/components-view";
export const metadata: Metadata = { title: "Component Catalogue" };
export default function ComponentsPage() { return <ComponentsView />; }
