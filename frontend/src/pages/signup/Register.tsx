import { SignupForm } from "@/components/auth/signup-form";
import BgImage from "../../../assests/img/bg_login1.jpg";

export default function SignupPage() {
  return (
    <div
      style={{
        backgroundImage: `url(${BgImage})`,
        backgroundRepeat: "no-repeat",
        backgroundPosition: "center",
        backgroundSize: "cover",
      }}
      className="bg-muted flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10"
    >
      <div className="flex w-full max-w-sm flex-col gap-6">
        <a
          href="#"
          className="flex  items-center gap-2 self-center font-medium"
        >
          Syncmark
        </a>
        <SignupForm />
      </div>
    </div>
  );
}
