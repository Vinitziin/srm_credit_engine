--
-- PostgreSQL database dump
--

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);

--
-- Name: cedentes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cedentes (
    name character varying(200) NOT NULL,
    document character varying(18) NOT NULL,
    id uuid NOT NULL
);

--
-- Name: currencies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.currencies (
    code character varying(3) NOT NULL,
    name character varying(50) NOT NULL,
    id uuid NOT NULL
);

--
-- Name: exchange_rates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.exchange_rates (
    from_currency_id uuid NOT NULL,
    to_currency_id uuid NOT NULL,
    rate numeric(20,8) NOT NULL,
    effective_date date NOT NULL,
    id uuid NOT NULL
);

--
-- Name: receivable_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.receivable_types (
    name character varying(100) NOT NULL,
    spread_rate numeric(10,6) NOT NULL,
    id uuid NOT NULL
);

--
-- Name: transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.transactions (
    cedente_id uuid NOT NULL,
    receivable_type_id uuid NOT NULL,
    face_value numeric(20,8) NOT NULL,
    present_value numeric(20,8) NOT NULL,
    currency_id uuid NOT NULL,
    payment_currency_id uuid NOT NULL,
    exchange_rate_used numeric(20,8),
    term_months integer NOT NULL,
    base_rate numeric(10,6) NOT NULL,
    spread_applied numeric(10,6) NOT NULL,
    status character varying(20) NOT NULL,
    version integer NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    id uuid NOT NULL
);

--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);

--
-- Name: cedentes cedentes_document_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cedentes
    ADD CONSTRAINT cedentes_document_key UNIQUE (document);

--
-- Name: cedentes cedentes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cedentes
    ADD CONSTRAINT cedentes_pkey PRIMARY KEY (id);

--
-- Name: currencies currencies_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.currencies
    ADD CONSTRAINT currencies_code_key UNIQUE (code);

--
-- Name: currencies currencies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.currencies
    ADD CONSTRAINT currencies_pkey PRIMARY KEY (id);

--
-- Name: exchange_rates exchange_rates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exchange_rates
    ADD CONSTRAINT exchange_rates_pkey PRIMARY KEY (id);

--
-- Name: receivable_types receivable_types_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.receivable_types
    ADD CONSTRAINT receivable_types_name_key UNIQUE (name);

--
-- Name: receivable_types receivable_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.receivable_types
    ADD CONSTRAINT receivable_types_pkey PRIMARY KEY (id);

--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);

--
-- Name: ix_exchange_rates_effective_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_exchange_rates_effective_date ON public.exchange_rates USING btree (effective_date);

--
-- Name: ix_exchange_rates_from_currency_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_exchange_rates_from_currency_id ON public.exchange_rates USING btree (from_currency_id);

--
-- Name: ix_exchange_rates_to_currency_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_exchange_rates_to_currency_id ON public.exchange_rates USING btree (to_currency_id);

--
-- Name: ix_transactions_cedente_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_transactions_cedente_id ON public.transactions USING btree (cedente_id);

--
-- Name: ix_transactions_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_transactions_created_at ON public.transactions USING btree (created_at);

--
-- Name: ix_transactions_currency_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_transactions_currency_id ON public.transactions USING btree (currency_id);

--
-- Name: ix_transactions_payment_currency_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_transactions_payment_currency_id ON public.transactions USING btree (payment_currency_id);

--
-- Name: exchange_rates exchange_rates_from_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exchange_rates
    ADD CONSTRAINT exchange_rates_from_currency_id_fkey FOREIGN KEY (from_currency_id) REFERENCES public.currencies(id);

--
-- Name: exchange_rates exchange_rates_to_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exchange_rates
    ADD CONSTRAINT exchange_rates_to_currency_id_fkey FOREIGN KEY (to_currency_id) REFERENCES public.currencies(id);

--
-- Name: transactions transactions_cedente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_cedente_id_fkey FOREIGN KEY (cedente_id) REFERENCES public.cedentes(id);

--
-- Name: transactions transactions_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_currency_id_fkey FOREIGN KEY (currency_id) REFERENCES public.currencies(id);

--
-- Name: transactions transactions_payment_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_payment_currency_id_fkey FOREIGN KEY (payment_currency_id) REFERENCES public.currencies(id);

--
-- Name: transactions transactions_receivable_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_receivable_type_id_fkey FOREIGN KEY (receivable_type_id) REFERENCES public.receivable_types(id);

--
-- PostgreSQL database dump complete
--

