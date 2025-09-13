--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ethnicity; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ethnicity (
    ethnicityid integer NOT NULL,
    ethniccode character varying(50),
    description character varying(255)
);


ALTER TABLE public.ethnicity OWNER TO postgres;

--
-- Name: ethnicity_ethnicityid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ethnicity_ethnicityid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ethnicity_ethnicityid_seq OWNER TO postgres;

--
-- Name: ethnicity_ethnicityid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ethnicity_ethnicityid_seq OWNED BY public.ethnicity.ethnicityid;


--
-- Name: hospital; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.hospital (
    orgid integer NOT NULL,
    orgname character varying(255),
    orgaddressline1 character varying(255),
    orgaddressline2 character varying(255),
    orgaddressline3 character varying(255),
    orgcity character varying(50),
    orgcountry character varying(50),
    orgpostcode character varying(20)
);


ALTER TABLE public.hospital OWNER TO postgres;

--
-- Name: hospital_organisationid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.hospital_organisationid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hospital_organisationid_seq OWNER TO postgres;

--
-- Name: hospital_organisationid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.hospital_organisationid_seq OWNED BY public.hospital.orgid;


--
-- Name: patient; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.patient (
    patientid integer NOT NULL,
    title character varying(10),
    firstname character varying(50),
    middlename character varying(50),
    lastname character varying(50),
    previous_lastname character varying(50),
    nhsnumber character varying(10),
    dob date,
    dod date,
    age integer,
    ethnicity character varying(255),
    sexual_orientation character varying(255)
);


ALTER TABLE public.patient OWNER TO postgres;

--
-- Name: patient_patientid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.patient_patientid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.patient_patientid_seq OWNER TO postgres;

--
-- Name: patient_patientid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.patient_patientid_seq OWNED BY public.patient.patientid;


--
-- Name: registration; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.registration (
    registrationid integer NOT NULL,
    dateregistration date,
    registrationstatus character varying(100),
    datedischarge date,
    patientid integer,
    orgid integer,
    reason_for_admission character varying(255)
);


ALTER TABLE public.registration OWNER TO postgres;

--
-- Name: registration_registrationid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.registration_registrationid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.registration_registrationid_seq OWNER TO postgres;

--
-- Name: registration_registrationid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.registration_registrationid_seq OWNED BY public.registration.registrationid;


--
-- Name: sexual_orientation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sexual_orientation (
    soid integer NOT NULL,
    soname character varying(50)
);


ALTER TABLE public.sexual_orientation OWNER TO postgres;

--
-- Name: sexual_orientation_soid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sexual_orientation_soid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sexual_orientation_soid_seq OWNER TO postgres;

--
-- Name: sexual_orientation_soid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sexual_orientation_soid_seq OWNED BY public.sexual_orientation.soid;


--
-- Name: ethnicity ethnicityid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ethnicity ALTER COLUMN ethnicityid SET DEFAULT nextval('public.ethnicity_ethnicityid_seq'::regclass);


--
-- Name: hospital orgid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hospital ALTER COLUMN orgid SET DEFAULT nextval('public.hospital_organisationid_seq'::regclass);


--
-- Name: patient patientid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patient ALTER COLUMN patientid SET DEFAULT nextval('public.patient_patientid_seq'::regclass);


--
-- Name: registration registrationid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration ALTER COLUMN registrationid SET DEFAULT nextval('public.registration_registrationid_seq'::regclass);


--
-- Name: sexual_orientation soid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sexual_orientation ALTER COLUMN soid SET DEFAULT nextval('public.sexual_orientation_soid_seq'::regclass);


--
-- Name: ethnicity ethnicity_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ethnicity
    ADD CONSTRAINT ethnicity_pkey PRIMARY KEY (ethnicityid);


--
-- Name: hospital hospital_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hospital
    ADD CONSTRAINT hospital_pkey PRIMARY KEY (orgid);


--
-- Name: patient patient_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patient
    ADD CONSTRAINT patient_pkey PRIMARY KEY (patientid);


--
-- Name: registration registration_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration
    ADD CONSTRAINT registration_pkey PRIMARY KEY (registrationid);


--
-- Name: sexual_orientation sexual_orientation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sexual_orientation
    ADD CONSTRAINT sexual_orientation_pkey PRIMARY KEY (soid);


--
-- Name: registration registration_orgid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration
    ADD CONSTRAINT registration_orgid_fkey FOREIGN KEY (orgid) REFERENCES public.hospital(orgid);


--
-- Name: registration registration_patientid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration
    ADD CONSTRAINT registration_patientid_fkey FOREIGN KEY (patientid) REFERENCES public.patient(patientid);


--
-- Name: TABLE ethnicity; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.ethnicity TO myuser;


--
-- Name: TABLE hospital; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.hospital TO myuser;


--
-- Name: TABLE patient; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.patient TO myuser;


--
-- Name: TABLE registration; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.registration TO myuser;


--
-- Name: TABLE sexual_orientation; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.sexual_orientation TO myuser;


--
-- PostgreSQL database dump complete
--

