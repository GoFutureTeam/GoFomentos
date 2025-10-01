import React, { useState, useEffect, useCallback } from "react";
import SearchInput from "./SearchInput";
import FilterDropdown from "./FilterDropdown";
import { useContextoEditaisPortugues } from "../hooks/useContextoEditaisPortugues";
import { FilterUpdate } from "../contexts/EditaisContextTypes";

interface FilterOption {
  id: string;
  label: string;
  checked: boolean;
}

interface FilterSectionProps {
  className?: string;
  onFiltersChange?: (filters: FilterUpdate) => void;
}

const FilterSection: React.FC<FilterSectionProps> = ({
  className,
  onFiltersChange,
}) => {
  // Buscar dados dos editais e estado atual dos filtros do contexto global
  const { allEditais, activeFilters } = useContextoEditaisPortugues();

  // Debug logs
  // console.log('🎯 FilterSection - allEditais recebidos:', allEditais?.length, allEditais);

  // Função para formatar labels dos filtros
  const formatFilterLabel = (
    text: string,
    isFinanciador: boolean = false
  ): string => {
    if (isFinanciador) {
      return text.toUpperCase();
    }
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
  };

  // Estados locais para os filtros
  const [areaFilters, setAreaFilters] = useState<FilterOption[]>([]);
  const [tipoRecursoFilters, setTipoRecursoFilters] = useState<FilterOption[]>(
    []
  );
  const [contrapartidaFilters, setContrapartidaFilters] = useState<
    FilterOption[]
  >([]);
  const [financiadorFilters, setFinanciadorFilters] = useState<FilterOption[]>(
    []
  );

  // Função para lidar com a busca por texto
  const handleSearch = (query: string) => {
    if (onFiltersChange) {
      onFiltersChange({
        search: query,
      });
    }
  };

  // Extrair áreas únicas dos editais
  const extractUniqueAreas = useCallback(() => {
    if (!allEditais || !Array.isArray(allEditais)) return [];
    const areasSet = new Set<string>();
    allEditais.forEach((edital) => {
      // Extrair de area_foco
      if (edital.area_foco) {
        const areas = edital.area_foco
          .split(",")
          .map((area) => area.trim())
          .filter((area) => area.length > 0);
        areas.forEach((area) => areasSet.add(area));
      }

      // Extrair de categoria como fallback
      if (edital.categoria) {
        const areas = edital.categoria
          .split(",")
          .map((area) => area.trim())
          .filter((area) => area.length > 0);
        areas.forEach((area) => areasSet.add(area));
      }
    });
    const uniqueAreas = Array.from(areasSet)
      .sort()
      .map((area, index) => ({
        id: `area-${index}-${area
          .toLowerCase()
          .replace(/[^a-z0-9]/g, "")}`,
        label: formatFilterLabel(area),
        checked: activeFilters.area.some((filterId) =>
          filterId.includes(
            area
              .toLowerCase()
              .replace(/[^a-z0-9]/g, "")
          )
        ),
      }));
    // console.log('🔍 Áreas extraídas:', uniqueAreas);
    return uniqueAreas;
  }, [allEditais, activeFilters.area]);

  // Extrair tipos de recursos únicos dos editais
  const extractUniqueTipoRecurso = useCallback(() => {
    if (!allEditais || !Array.isArray(allEditais)) return [];
    const tiposSet = new Set<string>();
    allEditais.forEach((edital) => {
      if (edital.tipo_recurso) {
        // Normalizar o valor removendo sufixos desnecessários
        const tipoLimpo = edital.tipo_recurso.replace(/\(A\)/gi, "").trim();
        if (tipoLimpo) {
          tiposSet.add(tipoLimpo);
        }
      }
    });
    const uniqueTipos = Array.from(tiposSet)
      .sort()
      .map((tipo, index) => ({
        id: `tipo-${index}-${tipo
          .toLowerCase()
          .replace(/[^a-z0-9]/g, "")}`,
        label: formatFilterLabel(tipo),
        checked: activeFilters.tipo_recurso.some((filterId) =>
          filterId.includes(
            tipo
              .toLowerCase()
              .replace(/[^a-z0-9]/g, "")
          )
        ),
      }));
    // console.log('💰 Tipos de Recurso extraídos:', uniqueTipos);
    return uniqueTipos;
  }, [allEditais, activeFilters.tipo_recurso]);

  // Extrair contrapartidas únicas dos editais
  const extractUniqueContrapartida = useCallback(() => {
    if (!allEditais || !Array.isArray(allEditais)) return [];
    const contrapartidasSet = new Set<string>();
    allEditais.forEach((edital) => {
      if (edital.tipo_contrapartida) {
        const contrapartida = edital.tipo_contrapartida.trim();
        if (contrapartida) {
          contrapartidasSet.add(contrapartida);
        }
      }
    });
    const uniqueContrapartidas = Array.from(contrapartidasSet)
      .sort()
      .map((contrapartida, index) => ({
        id: `contrapartida-${index}-${contrapartida
          .toLowerCase()
          .replace(/[^a-z0-9]/g, "")}`,
        label: formatFilterLabel(contrapartida),
        checked: activeFilters.contrapartida.some((filterId) =>
          filterId.includes(
            contrapartida
              .toLowerCase()
              .replace(/[^a-z0-9]/g, "")
          )
        ),
      }));
    // console.log('🤝 Contrapartidas extraídas:', uniqueContrapartidas);
    return uniqueContrapartidas;
  }, [allEditais, activeFilters.contrapartida]);

  // Extrair financiadores únicos dos editais
  const extractUniqueFinanciadores = useCallback(() => {
    if (!allEditais || !Array.isArray(allEditais)) return [];
    const financiadoresSet = new Set<string>();
    allEditais.forEach((edital) => {
      if (edital.financiador_1) {
        financiadoresSet.add(edital.financiador_1.trim());
      }
      if (edital.financiador_2) {
        financiadoresSet.add(edital.financiador_2.trim());
      }
    });
    const uniqueFinanciadores = Array.from(financiadoresSet)
      .sort()
      .map((financiador, index) => ({
        id: `financiador-${index}-${financiador
          .toLowerCase()
          .replace(/[^a-z0-9]/g, "")}`,
        label: formatFilterLabel(financiador, true),
        checked: activeFilters.financiador.some((filterId) =>
          filterId.includes(
            financiador
              .toLowerCase()
              .replace(/[^a-z0-9]/g, "")
          )
        ),
      }));
    // console.log('🏦 Financiadores extraídos:', uniqueFinanciadores);
    return uniqueFinanciadores;
  }, [allEditais, activeFilters.financiador]);

  // Atualizar todos os filtros quando editais ou filtros ativos mudarem
  useEffect(() => {
    if (allEditais && allEditais.length > 0) {
      setAreaFilters(extractUniqueAreas());
      setTipoRecursoFilters(extractUniqueTipoRecurso());
      setContrapartidaFilters(extractUniqueContrapartida());
      setFinanciadorFilters(extractUniqueFinanciadores());
    }
  }, [
    allEditais,
    extractUniqueAreas,
    extractUniqueTipoRecurso,
    extractUniqueContrapartida,
    extractUniqueFinanciadores,
  ]);

  // Função para notificar mudanças nos filtros
  const notifyFiltersChange = (
    newAreaFilters: FilterOption[],
    newTipoRecursoFilters: FilterOption[],
    newContrapartidaFilters: FilterOption[],
    newFinanciadorFilters: FilterOption[]
  ) => {
    if (onFiltersChange) {
      // Extract selected filter IDs
      const selectedAreaIds = newAreaFilters
        .filter((f) => f.checked)
        .map((f) => f.id);
      const selectedTipoRecursoIds = newTipoRecursoFilters
        .filter((f) => f.checked)
        .map((f) => f.id);
      const selectedContrapartidaIds = newContrapartidaFilters
        .filter((f) => f.checked)
        .map((f) => f.id);
      const selectedFinanciadorIds = newFinanciadorFilters
        .filter((f) => f.checked)
        .map((f) => f.id);

      // Notify parent component of filter changes
      onFiltersChange({
        filters: {
          area: selectedAreaIds,
          tipo_recurso: selectedTipoRecursoIds,
          contrapartida: selectedContrapartidaIds,
          financiador: selectedFinanciadorIds,
        },
      });
    }
  };

  // Handlers para mudanças nos filtros
  const handleAreaFilterChange = (optionId: string, checked: boolean) => {
    const updatedFilters = areaFilters.map((filter) => {
      if (filter.id === optionId) {
        return { ...filter, checked };
      }
      return filter;
    });
    setAreaFilters(updatedFilters);
    notifyFiltersChange(
      updatedFilters,
      tipoRecursoFilters,
      contrapartidaFilters,
      financiadorFilters
    );
  };

  const handleTipoRecursoFilterChange = (
    optionId: string,
    checked: boolean
  ) => {
    const updatedFilters = tipoRecursoFilters.map((filter) => {
      if (filter.id === optionId) {
        return { ...filter, checked };
      }
      return filter;
    });
    setTipoRecursoFilters(updatedFilters);
    notifyFiltersChange(
      areaFilters,
      updatedFilters,
      contrapartidaFilters,
      financiadorFilters
    );
  };

  const handleContrapartidaFilterChange = (
    optionId: string,
    checked: boolean
  ) => {
    const updatedFilters = contrapartidaFilters.map((filter) => {
      if (filter.id === optionId) {
        return { ...filter, checked };
      }
      return filter;
    });
    setContrapartidaFilters(updatedFilters);
    notifyFiltersChange(
      areaFilters,
      tipoRecursoFilters,
      updatedFilters,
      financiadorFilters
    );
  };

  const handleFinanciadorFilterChange = (
    optionId: string,
    checked: boolean
  ) => {
    const updatedFilters = financiadorFilters.map((filter) => {
      if (filter.id === optionId) {
        return { ...filter, checked };
      }
      return filter;
    });
    setFinanciadorFilters(updatedFilters);
    notifyFiltersChange(
      areaFilters,
      tipoRecursoFilters,
      contrapartidaFilters,
      updatedFilters
    );
  };

  // Handlers para "Selecionar Todos"
  const handleSelectAllArea = (selectAll: boolean) => {
    const updatedFilters = areaFilters.map(filter => ({
      ...filter,
      checked: selectAll
    }));
    setAreaFilters(updatedFilters);
    notifyFiltersChange(
      updatedFilters,
      tipoRecursoFilters,
      contrapartidaFilters,
      financiadorFilters
    );
  };

  const handleSelectAllTipoRecurso = (selectAll: boolean) => {
    const updatedFilters = tipoRecursoFilters.map(filter => ({
      ...filter,
      checked: selectAll
    }));
    setTipoRecursoFilters(updatedFilters);
    notifyFiltersChange(
      areaFilters,
      updatedFilters,
      contrapartidaFilters,
      financiadorFilters
    );
  };

  const handleSelectAllContrapartida = (selectAll: boolean) => {
    const updatedFilters = contrapartidaFilters.map(filter => ({
      ...filter,
      checked: selectAll
    }));
    setContrapartidaFilters(updatedFilters);
    notifyFiltersChange(
      areaFilters,
      tipoRecursoFilters,
      updatedFilters,
      financiadorFilters
    );
  };

  const handleSelectAllFinanciador = (selectAll: boolean) => {
    const updatedFilters = financiadorFilters.map(filter => ({
      ...filter,
      checked: selectAll
    }));
    setFinanciadorFilters(updatedFilters);
    notifyFiltersChange(
      areaFilters,
      tipoRecursoFilters,
      contrapartidaFilters,
      updatedFilters
    );
  };

  return (
    <section
      className={`bg-white flex w-full px-5 py-12 lg:px-[100px] lg:py-[62px] ${
        className || ""
      }`}
    >
      <div className="w-full max-w-[1279px] mx-auto">
        <div className="flex justify-between items-center mb-[30px]">
          <h2 className="text-[#435058] text-2xl sm:text-3xl font-extrabold py-0">
            Explore aqui os Editais disponíveis
          </h2>

          <div className="w-full max-w-[400px] items-center">
            <SearchInput onSearch={handleSearch} />
          </div>
        </div>
        <div className="mt-[30px] flex gap-[20px]">
          <div className="w-full max-w-[400px]">
            <p className="text-[#435058] text-2xl sm:text-3xl font-extrabold py-0 mb-[15px] ml-6">
              Área dos editais
            </p>
            <div className="w-full bg-gray-100 rounded-3xl p-6 min-h-[200px] max-h-[400px] overflow-y-auto">
              <div className="w-full">
                <FilterDropdown
                  title="Selecione a área do edital"
                  options={areaFilters}
                  onFilterChange={handleAreaFilterChange}
                  onSelectAll={handleSelectAllArea}
                  iconSrc=""
                />
              </div>
            </div>
          </div>
          <div className="w-full items-center">
            <p className="text-[#435058] text-2xl sm:text-3xl font-extrabold py-0 mb-[15px] ml-6">
              Filtros avançados
            </p>
            <div className="flex w-full justify-center gap-[20px] lg:gap-[30px] bg-gray-100 rounded-3xl p-6 min-h-[200px] max-h-[400px] overflow-y-auto">
              <div className="w-full">
                <FilterDropdown
                  title="Tipo de Recurso"
                  options={tipoRecursoFilters}
                  onFilterChange={handleTipoRecursoFilterChange}
                  onSelectAll={handleSelectAllTipoRecurso}
                  iconSrc=""
                />
              </div>

              <div className="w-full">
                <FilterDropdown
                  title="Contrapartida"
                  options={contrapartidaFilters}
                  onFilterChange={handleContrapartidaFilterChange}
                  onSelectAll={handleSelectAllContrapartida}
                  iconSrc=""
                />
              </div>

              <div className="w-full">
                <FilterDropdown
                  title="Financiador"
                  options={financiadorFilters}
                  onFilterChange={handleFinanciadorFilterChange}
                  onSelectAll={handleSelectAllFinanciador}
                  iconSrc=""
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
export default FilterSection;
