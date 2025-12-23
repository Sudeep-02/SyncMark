export default function ErrorState({ message }: { message: string }) {
  return <div className="p-6 text-center text-red-500">{message}</div>;
}
