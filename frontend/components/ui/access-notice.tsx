import { Icon } from "@/components/icon";

export function AccessNotice({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <aside className="access-notice" role="note">
      <span><Icon name="shield" size={19} /></span>
      <div><strong>{title}</strong><p>{description}</p></div>
    </aside>
  );
}
