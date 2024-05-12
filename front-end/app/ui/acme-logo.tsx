import Image from "next/image";

export default function AcmeLogo() {
  return (
    <Image
      src="/nurol_logo.png"
      priority
      alt={`Nurol Logo`}
      width={150}
      height={150}
    />
  );
}
