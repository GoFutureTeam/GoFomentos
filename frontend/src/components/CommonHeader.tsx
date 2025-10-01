import React from "react";
import { useLocation, Link } from "react-router-dom";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import Header from "./Header";
interface CommonHeaderProps {
  title?: string;
  description?: string;
  showSecondSection?: boolean;
}
const CommonHeader: React.FC<CommonHeaderProps> = ({
  title = "Soluções para alavancar a inovação em sua empresa",
  description = "Conheça os instrumentos de apoio à inovação disponíveis e selecione os mais adequados ao seu projeto.",
  showSecondSection = true,
}) => {
  const location = useLocation();

  // Gerar breadcrumb baseado na rota atual (sem o item Inicio)
  const getBreadcrumbItems = () => {
    const path = location.pathname.split("/").filter(Boolean);

    const breadcrumbItems = path.map((segment, index) => {
      const isActive = index === path.length - 1;
      
      // Se o segmento for "edital" e não for o último (ativo), redirecionar para início
      let href = `/${path.slice(0, index + 1).join("/")}`;
      if (segment.toLowerCase() === "edital" && !isActive) {
        href = "/";
      }

      // Formatar o label corretamente
      let label = segment.charAt(0).toUpperCase() + segment.slice(1);
      
      // Substituir hífens por espaços e capitalizar cada palavra
      if (segment.includes('-')) {
        label = segment
          .split('-')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');
      }

      return {
        label,
        href,
        isActive,
      };
    });

    // Retornar apenas os breadcrumbItems, SEM adicionar "Inicio"
    return breadcrumbItems;
  };
  const breadcrumbItems = getBreadcrumbItems();
  return (
    <>
      <Header />

      <section className="bg-[rgba(67,80,88,1)]">
        <div
          style={{
            backgroundImage:
              "url(/lovable-uploads/fc8e9f15-312d-4438-9834-cd7b3554cb1d.png)",
            backgroundSize: "auto 100%",
            backgroundPosition: "right center",
            backgroundRepeat: "no-repeat",
          }}
          className="px-5 py-12 lg:py-16 relative"
        >
          <div className="w-full max-w-[1279px] mx-auto px-0 lg:px-5">
            {breadcrumbItems.length > 0 && (
              <Breadcrumb className="mb-8">
                <BreadcrumbList className="text-[rgba(248,248,248,1)] text-base sm:text-lg font-medium">
                  {breadcrumbItems
                    .map((item, index) => [
                      <BreadcrumbItem key={`item-${index}`}>
                        {item.isActive ? (
                          <BreadcrumbPage className="text-[rgba(248,248,248,1)]">
                            {item.label}
                          </BreadcrumbPage>
                        ) : (
                          <BreadcrumbLink
                            asChild
                            className="text-[rgba(248,248,248,1)] hover:text-white"
                          >
                            <Link to={item.href}>{item.label}</Link>
                          </BreadcrumbLink>
                        )}
                      </BreadcrumbItem>,
                      index < breadcrumbItems.length - 1 && (
                        <BreadcrumbSeparator
                          key={`separator-${index}`}
                          className="text-[rgba(248,248,248,1)]"
                        />
                      ),
                    ])
                    .flat()
                    .filter(Boolean)}
                </BreadcrumbList>
              </Breadcrumb>
            )}

            <div className="flex gap-8 flex-col lg:flex-row items-center">
              <div className="w-full lg:w-[65%]">
                <h1 className="text-[rgba(248,248,248,1)] text-4xl sm:text-5xl font-black leading-tight tracking-wide mb-6 lg:text-5xl">
                  {title}
                </h1>
                {description && (
                  <p className="text-[rgba(248,248,248,1)] text-xl font-medium leading-relaxed">
                    {description}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {showSecondSection && (
          <div
            style={{
              backgroundImage:
                "url(/lovable-uploads/8a170130-d07b-497a-9e68-ec6bb3ce56bb.png)",
              backgroundSize: "cover",
              backgroundPosition: "center",
              backgroundRepeat: "no-repeat",
            }}
            className="relative bg-[rgba(220,247,99,0.65)] z-10 flex w-full flex-col items-center py-12 sm:py-16 px-5 lg:py-[20px]"
          >
            <div className="flex w-full max-w-[1279px] flex-row justify-between items-start gap-8 px-0 lg:px-5">
              <h2 className="font-archivo font-extrabold text-2xl sm:text-3xl lg:w-[273px] lg:shrink-0 text-[rgba(67,80,88,1)] mx-0 my-0 text-left px-0 lg:text-3xl py-[6px]">
                Você sabe porque se inscrever em Editais?
              </h2>
              <p className="font-archivo font-medium text-lg sm:text-xl leading-6 sm:leading-[30px] max-w-[550px] text-[rgba(67,80,88,1)] py-[6px]">
                Participar de editais de fomento é uma das formas mais
                estratégicas de captar recursos, expandir projetos inovadores e
                ganhar visibilidade no seu setor. Com o Radar de Fomentos, você
                encontra as melhores oportunidades em um só lugar, com clareza e
                agilidade.
              </p>
            </div>
          </div>
        )}
      </section>
    </>
  );
};
export default CommonHeader;
