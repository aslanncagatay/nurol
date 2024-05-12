import Table from "@/app/ui/departments/table";
import { CreateDepartment } from "@/app/ui/departments/buttons";
import { lusitana } from "@/app/ui/fonts";
import { DepartmentsTableSkeleton } from "@/app/ui/skeletons";
import { Suspense } from "react";
import { Metadata } from "next";
import { getDepartments } from "../lib/api/departments";
import Form from "../ui/rabbitmq/create-form";

export const metadata: Metadata = {
  title: "Departments",
};

export default async function Page() {
  const departments = await getDepartments();

  return (
    <div className="w-full">
      <div className="flex w-full items-center justify-between">
        <h1 className={`${lusitana.className} text-2xl`}>RabbitMQ</h1>
      </div>
      <div className="mt-4">
        <Form />
      </div>
    </div>
  );
}
