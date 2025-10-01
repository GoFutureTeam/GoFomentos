import React from 'react';
import { useNavigate } from 'react-router-dom';

export const MonitoringSection: React.FC = () => {
  const navigate = useNavigate();
  
  const handleMonitoringSignup = () => {
    navigate('/email-signup');
  };
  return <section className="bg-[rgba(67,80,88,1)] shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] mt-8 px-[50px] py-[30px] rounded-[39px] max-md:max-w-full max-md:mt-8 max-md:px-5">
      <div className="gap-5 flex max-md:flex-col max-md:items-stretch">
        <div className="w-[67%] max-md:w-full max-md:ml-0">
          <h3 className="text-white text-[26px] font-extrabold self-stretch max-md:max-w-full max-md:mt-10 text-left my-[15px]">
            Quer ser avisado automaticamente sempre que um edital compatível surgir?
          </h3>
        </div>
        <div className="w-[33%] ml-5 max-md:w-full max-md:ml-0">
          <button onClick={handleMonitoringSignup} className="bg-neutral-50 shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] grow text-xl text-[rgba(67,80,88,1)] font-bold text-center w-full pt-[17px] pb-[29px] px-[53px] rounded-[35px] max-md:mt-10 max-md:px-5 hover:bg-gray-100 transition-colors">
            Cadastrar para monitoramento!
          </button>
        </div>
      </div>
    </section>;
};