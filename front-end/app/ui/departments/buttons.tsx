import {
  ArrowLeftCircleIcon,
  PlusIcon,
  MagnifyingGlassIcon,
} from "@heroicons/react/24/outline";
import Link from "next/link";

export function CreateDepartment() {
  return (
    <Link
      href="/departments/create"
      className="flex h-10 items-center rounded-lg bg-blue-600 px-4 text-sm font-medium text-white transition-colors hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
    >
      <span className="hidden md:block">Create New</span>{" "}
      <PlusIcon className="h-5 md:ml-4" />
    </Link>
  );
}

export function ReturnBack() {
  return (
    <Link
      href="/departments"
      className="flex h-10 items-center rounded-lg bg-blue-600 px-4 text-sm font-medium text-white transition-colors hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
    >
      <ArrowLeftCircleIcon className="h-5" />{" "}
      <span className="hidden md:block ml-3">Geri Dön</span>
    </Link>
  );
}

export function ViewEmployees({ id }: { id: number }) {
  return (
    <Link href={`/departments/${id}`} className="p-2">
      <MagnifyingGlassIcon className="w-5" />
    </Link>
  );
}
