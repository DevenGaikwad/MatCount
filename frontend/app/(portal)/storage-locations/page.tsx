import type { Metadata } from "next";
import { StorageView } from "@/features/master-data/storage-view";
export const metadata: Metadata = { title: "Storage Locations" };
export default function StoragePage() { return <StorageView />; }
