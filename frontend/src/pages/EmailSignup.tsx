import React from 'react';
import CommonHeader from '../components/CommonHeader';
import { EmailSignup as EmailSignupForm } from '../components/match/EmailSignup';
import Footer from '../components/details/Footer';
import { uploads } from '../assets/uploads';

const EmailSignup = () => {
  return (
    <div className="overflow-hidden">
      <CommonHeader 
        title="Cadastre-se e receba atualizações no seu e-mail"
        description="Cadastre seu email e seja notificado automaticamente sempre que um novo edital compatível com seu projeto for publicado!"
        showSecondSection={false}
      />
      

      
      <main>
        <EmailSignupForm />
      </main>
      
      <Footer />
    </div>
  );
};

export default EmailSignup;