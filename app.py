#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Main app."""

import os
import itertools
import re
import pandas as pd
import threading
import datetime
from flask import Flask, render_template, request, jsonify, flash, \
    send_from_directory  # make_response, ufl_for
from random import randint
from random import randrange
from operator import itemgetter
from models import dbQuery, pyChart, Outreach, geocode as geo
from DLeeCious import quotify, clausify, PurrtySQL, PurrtyJSON
from werkzeug import secure_filename

# INIT VARIABLES #
filepath = "I:/Health Business Operations/Delivery Systems Informatics/Network Financial Performance/Leequid/Python/HD Engagement"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(filepath, "var", "uploads")
app.config['STATIC_FOLDER'] = os.path.join(filepath, "static")
app.config['TEMPLATE_FOLDER'] = os.path.join(filepath, "templates")
app.config['ALLOWED_EXTENSIONS'] = set(['csv', 'xlsx'])
app.secret_key = 'DDD'


def allowed_file(filename, fext):
    """Return a boolean value if filename has the extension.

    Arguments:

    """
    return '.' in filename and filename.rsplit('.', 1)[1] in fext


@app.route('/')
@app.route('/index')
def index():
    """Return home page."""
    return render_template('index.html', title='Home')


#     $$$$$$$\   $$$$$$\   $$$$$$\  $$\   $$\ $$$$$$$\   $$$$$$\   $$$$$$\  $$$$$$$\  $$$$$$$\   $$$$$$\
#     $$  __$$\ $$  __$$\ $$  __$$\ $$ |  $$ |$$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\
#     $$ |  $$ |$$ /  $$ |$$ /  \__|$$ |  $$ |$$ |  $$ |$$ /  $$ |$$ /  $$ |$$ |  $$ |$$ |  $$ |$$ /  \__|
#     $$ |  $$ |$$$$$$$$ |\$$$$$$\  $$$$$$$$ |$$$$$$$\ |$$ |  $$ |$$$$$$$$ |$$$$$$$  |$$ |  $$ |\$$$$$$\
#     $$ |  $$ |$$  __$$ | \____$$\ $$  __$$ |$$  __$$\ $$ |  $$ |$$  __$$ |$$  __$$< $$ |  $$ | \____$$\
#     $$ |  $$ |$$ |  $$ |$$\   $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$\   $$ |
#     $$$$$$$  |$$ |  $$ |\$$$$$$  |$$ |  $$ |$$$$$$$  | $$$$$$  |$$ |  $$ |$$ |  $$ |$$$$$$$  |\$$$$$$  |
#     \_______/ \__|  \__| \______/ \__|  \__|\_______/  \______/ \__|  \__|\__|  \__|\_______/  \______/
#
#
#
@app.route('/hd', methods=['GET', 'POST'])
def hdEngReport():
    if request.method == 'POST':
        # initialize group list var
        group_list = []
        group_clause = ""

        # fetch form vars
        startdt = request.form['startdt']
        enddt = request.form['enddt']
        group = request.form.getlist('group')

        # add to group list based on what groups were selected in the form
        if 'FB' in group:
            group_list.append('70395')
            group_clause = group_clause + clausify("when GP_NB in ('70395') then 'FB Employee Grp'", 4)
        if 'FLCons' in group:
            group_list = group_list + ['31980', '41934', '78801', '78803', '78804', '78805', '78806',
                                       '78808', '78809', '78811', '78812', '78813', '78814', '78816',
                                       '78819', '78820', '78821', '78822', '78824', '78826', '78827',
                                       '92727', '16087']
            group_clause = group_clause + clausify("when GP_NB in ('31980','41934','78801','78803','78804','78805','78806','78808','78809','78811','78812','78813','78814','78816','78819','78820','78821','78822','78824','78826','78827','92727','16087') then 'FL Consortium'", 4)
        if 'Gator' in group:
            group_list = group_list + ['66125', 'B2594', '64601', 'B2655', '15092', 'B4829', 'B4830',
                                       'B4831', '39159', 'B4550', 'A9918', '78358', 'B3158']
            group_clause = group_clause + clausify("when GP_NB in ('66125','B2594','64601','B2655','15092','B4829','B4830','B4831','39159','B4550','A9918','78358','B3158') then 'GatorCare'", 4)
        if 'Polk' in group:
            group_list.append('60435')
            group_clause = group_clause + clausify("when GP_NB in ('60435') then 'Polk School Board'", 4)
        if 'State' in group:
            group_list = group_list + ['76402', '76444', '76442']
            group_clause = group_clause + clausify("when GP_NB in ('76402','76444','76442') then 'State Account'", 4)
        if 'FEP' in group:
            group_list.append('G0000')
            group_clause = group_clause + clausify("when GP_NB in ('G0000') then 'FEP'", 4)

        # fetch optional form vars
        try:
            group_nb = re.sub(r'[^A-Z0-9]', " ", request.form['groupnb'].upper()).split()
            group_list = group_list + group_nb
        except:
            pass
        try:
            hirisk = request.form['hirisk']
        except:
            hirisk = '0'
        try:
            devmode = request.form['devmode']
        except:
            devmode = '0'

        # add an additional SQL clause if high risk is checked
        if hirisk == '1':
            clause = "and DACL_HGH_RSK_IN = '1'"
        else:
            clause = "--and DACL_HGH_RSK_IN = '1'"

        # read the SQL file for pulling the data
        file = open(os.path.join(app.config['STATIC_FOLDER'], 'sql', 'HDEng.sql'), 'r')
        query = file.read()
        file.close()

        # inject paramters into the SQL query
        query_format = (quotify(startdt), quotify(enddt), ','.join(['?'] * len(group_list)), clausify(clause, 3), group_clause)
        params = list(itertools.chain.from_iterable([group_list]))

        result = dbQuery(query.format(*query_format), 'edw', params)

        # create chart objects for passing into template
        chart1 = pyChart('column', 'chart1', 'Total Membership by Group Number', xLab=[value for value in result['GROUP']], yLab='Total Members')
        chart1.addToSeries('Total Membership', [row[0] for row in result[['TOTAL_MEMBERS']].itertuples(False)])

        chart2 = pyChart('column', 'chart2', 'Attempted/Reached/Engaged', xLab=[value for value in result['GROUP']], yLab='Count')
        chart2.addToSeries('Attempted', [row[0] for row in result[['MBR_ATTEMPTED']].itertuples(False)])
        chart2.addToSeries('Reached', [row[0] for row in result[['MBR_REACHED']].itertuples(False)])
        chart2.addToSeries('Engaged', [row[0] for row in result[['MBR_ENGAGED']].itertuples(False)])

        # generate charts
        charts = {}
        charts[1] = chart1.generate()
        charts[2] = chart2.generate()

        # Purrtify for rendering SQL code if developer mode is checked
        if devmode == '1':
            code_format = (quotify(startdt), quotify(enddt), ",".join([quotify(grp) for grp in group_list]), clausify(clause, 3), group_clause)
            code = PurrtySQL(query.format(*code_format))
        else:
            code = ''

        # render template
        return render_template('render.html', result=result, startdt=startdt, enddt=enddt, hirisk=hirisk, devmode=devmode, code=code,
                               summed=result.sum(numeric_only=True), charts=charts, title='HD Engagement Report')

    # render this template if method was GET
    return render_template('hdengform.html', title='HD Engagement Report')


@app.route('/shd')
def shd():
    datasets = pd.read_csv(os.path.join(app.config['STATIC_FOLDER'], 'data', 'dsihealth_datasets.csv'))
    return render_template('SHD.html', datasets=datasets, title='Sandbox Hog Dashboard')


@app.route('/dm', methods=['GET', 'POST'])
def dmEng():
    if request.method == 'POST':
        file = request.files['file']
        memField = request.form['memField']

        if file and allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
            filename = secure_filename(file.filename)

            hash = '%030x' % randrange(16**30)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], hash))

            if filename.rsplit('.', 1)[1] == 'xlsx':
                uploaded = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], hash))
            elif filename.rsplit('.', 1)[1] == 'csv':
                uploaded = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], hash))

            file = open(os.path.join(app.config['STATIC_FOLDER'], 'sql', 'DMEng.sql'), 'r')
            query = file.read()
            file.close()

            dmlist = dbQuery(query, 'jiva')

            result = uploaded.merge(dmlist, left_on=memField, right_on='MEMBER_ID', how='left')

            return render_template('core.html', result=result, title='DM Engagement')
        elif not file:
            flash('A file is required', 'alert-warning')
            return render_template('core.html', result=None, title='DM Engagement')
        else:
            flash('Invalid file type', 'alert-warning')
            return render_template('core.html', result=None, title='DM Engagement')

    return render_template('core.html', result=None, title='DM Engagement')


@app.route('/roi', methods=['GET', 'POST'])
def roi():
    if request.method == 'POST':
        # fetch form vars
        program = request.form['program']
        prog_cost = int(request.form['progcost'])

        # read ROI output
        dataset = pd.read_csv(os.path.join(app.config['STATIC_FOLDER'], 'data', 'cmdm_dataset.csv'))

        # fetch yyyymm
        try:
            yyyymm = int(request.form['yyyymm'])
        except:
            yyyymm = dataset['END_YRMO'].max()

        # fetch lobs
        # lobs = request.form.getlist('LOB')
        lobs = list(pd.unique(dataset[['LOB']].values.ravel()))

        # generate data result for charts
        result = dataset[(dataset['PROG'] == program) & (dataset['LOB'].isin(lobs))]

        # get only the columns needed
        result = result[['END_YRMO', 'PERIOD', 'LOB', 'PROG', 'TYPE', 'SERVICE_CAT', 'PVAL', 'GOALS_MET', 'LSMean']]

        # get unique YYYYMM from dataset
        unique_yyyymm = list(pd.unique(result[['END_YRMO']].values.ravel()))

        # split cost and util
        costResult = result[result['TYPE'] == 'COST']
        utilResult = result[result['TYPE'] == 'COUNT']

        # create a mapping dictionary
        mapper = {1: ['Medical', 'TOTAL MEDICAL'],
                  2: ['RX', 'PHARMACY'],
                  3: ['Ancillary', 'ANCILLARY'],
                  4: ['ER', 'ER'],
                  5: ['Home Health', 'HOME HEALTH'],
                  6: ['Inpatient', 'INPATIENT'],
                  7: ['Lab', 'LABORATORY'],
                  8: ['Other Prof', 'OTHER PROFESSIONAL'],
                  9: ['Outpatient', 'OUTPATIENT'],
                  10: ['Office Visit', 'PROFESSIONAL OFFICE VISIT'],
                  11: ['Radiology', 'RADIOLOGY'],
                  12: ['Total', 'TOTAL ALL']}

        # create chart objects for passing into template
        costCharts = {}
        utilCharts = {}

        for lob in lobs:
            costCharts[lob] = {}
            utilCharts[lob] = {}
            for i in range(len(mapper)):
                if i == 0:
                    costCharts[lob][i + 1] = pyChart('line', 'costChart{0}_{1}'.format(i + 1, lob), ' '.join(['Expected Post', mapper[i + 1][0], 'Cost']), xLab=unique_yyyymm, yLab='Cost')
                    costCharts[lob][i + 1].addToSeries('Control', [row[0] for row in costResult[(costResult['GOALS_MET'] == 0) & (costResult['SERVICE_CAT'] == mapper[i + 1][1]) & (costResult['LOB'] == lob)][['LSMean']].itertuples(False)])
                    costCharts[lob][i + 1].addToSeries('Engaged', [row[0] for row in costResult[(costResult['GOALS_MET'] == 1) & (costResult['SERVICE_CAT'] == mapper[i + 1][1]) & (costResult['LOB'] == lob)][['LSMean']].itertuples(False)])
                    costCharts[lob][i + 1].formatPoint('{series.name}: <b>${point.y:,.0f}</b><br/>')
                    costCharts[lob][i + 1] = costCharts[lob][i + 1].generate()
                else:
                    costCharts[lob][i + 1] = pyChart('line', 'costChart{0}_{1}'.format(i + 1, lob), ' '.join(['Expected Post', mapper[i + 1][0], 'Cost']), xLab=unique_yyyymm, yLab='Cost')
                    utilCharts[lob][i + 1] = pyChart('line', 'utilChart{0}_{1}'.format(i + 1, lob), ' '.join(['Expected Post', mapper[i + 1][0], 'Utilization']), xLab=unique_yyyymm, yLab='Utilization')
                    costCharts[lob][i + 1].addToSeries('Control', [row[0] for row in costResult[(costResult['GOALS_MET'] == 0) & (costResult['SERVICE_CAT'] == mapper[i + 1][1]) & (costResult['LOB'] == lob)][['LSMean']].itertuples(False)])
                    costCharts[lob][i + 1].addToSeries('Engaged', [row[0] for row in costResult[(costResult['GOALS_MET'] == 1) & (costResult['SERVICE_CAT'] == mapper[i + 1][1]) & (costResult['LOB'] == lob)][['LSMean']].itertuples(False)])
                    utilCharts[lob][i + 1].addToSeries('Control', [row[0] for row in utilResult[(utilResult['GOALS_MET'] == 0) & (utilResult['SERVICE_CAT'] == mapper[i + 1][1]) & (utilResult['LOB'] == lob)][['LSMean']].itertuples(False)])
                    utilCharts[lob][i + 1].addToSeries('Engaged', [row[0] for row in utilResult[(utilResult['GOALS_MET'] == 1) & (utilResult['SERVICE_CAT'] == mapper[i + 1][1]) & (utilResult['LOB'] == lob)][['LSMean']].itertuples(False)])
                    costCharts[lob][i + 1].formatPoint('{series.name}: <b>${point.y:,.0f}</b><br/>')
                    utilCharts[lob][i + 1].formatPoint('{series.name}: <b>{point.y:,.2f}</b><br/>')
                    costCharts[lob][i + 1] = costCharts[lob][i + 1].generate()
                    utilCharts[lob][i + 1] = utilCharts[lob][i + 1].generate()

        # get data result for rendering to table
        table_data = pd.pivot_table(result[result['END_YRMO'] == yyyymm], index=['END_YRMO', 'PERIOD', 'LOB', 'PROG', 'TYPE', 'SERVICE_CAT', 'PVAL'], columns='GOALS_MET', values='LSMean').reset_index()
        table_data = table_data.rename(columns={0: 'CONTROL', 1: 'ENGAGED'})
        table_data['DIFF'] = table_data['CONTROL'] - table_data['ENGAGED']
        cost_table = table_data[table_data['TYPE'] == 'COST']
        util_table = table_data[table_data['TYPE'] == 'COUNT']

        # define columns and order to output for the generated table
        cols = ['SERVICE_CAT', 'CONTROL', 'ENGAGED', 'DIFF', 'PVAL']

        # get engaged counts for calculating total savings
        eng_ct = pd.read_csv(os.path.join(app.config['STATIC_FOLDER'], 'data', 'cmdm_engaged.csv'))
        eng_ct = eng_ct[(eng_ct['PROG'] == program) & (eng_ct['END_YRMO'] == yyyymm)]

        # calculate ROI
        total_savings = 0
        for lob in lobs:
            total_savings = total_savings + eng_ct.loc[eng_ct['LOB'] == lob, 'ENGAGED_CT'].values[0] * cost_table.loc[(cost_table['LOB'] == lob) & (cost_table['SERVICE_CAT'] == 'TOTAL ALL'), 'DIFF'].values[0]

        # render template
        return render_template('roi.html', result=[costCharts, utilCharts], data=[cost_table, util_table], program=program, yrmo=yyyymm, cols=cols, prog_cost=prog_cost, total_savings=total_savings, title='ROI')

    return render_template('roi.html', result=None, title='ROI')


#     $$$$$$$\  $$$$$$$$\ $$\      $$\  $$$$$$\   $$$$$$\
#     $$  __$$\ $$  _____|$$$\    $$$ |$$  __$$\ $$  __$$\
#     $$ |  $$ |$$ |      $$$$\  $$$$ |$$ /  $$ |$$ /  \__|
#     $$ |  $$ |$$$$$\    $$\$$\$$ $$ |$$ |  $$ |\$$$$$$\
#     $$ |  $$ |$$  __|   $$ \$$$  $$ |$$ |  $$ | \____$$\
#     $$ |  $$ |$$ |      $$ |\$  /$$ |$$ |  $$ |$$\   $$ |
#     $$$$$$$  |$$$$$$$$\ $$ | \_/ $$ | $$$$$$  |\$$$$$$  |
#     \_______/ \________|\__|     \__| \______/  \______/
#
#
#
@app.route('/geocode', methods=['GET', 'POST'])
def geocode():
    if request.method == 'POST':
        address = request.form['address']
        location = geo(address)
        return render_template('geocode.html', address=address, location=location, title='Geocoding Demo')

    return render_template('geocode.html', address=None, title='Geocoding Demo')


@app.route('/outreach', methods=['GET', 'POST'])
def outreach():
    raw = {'Member': ['Armin van Purren', 'Harry Pawtter', 'Tayroar Swift', 'Valdimeow Purrtin', 'Barack Oclawma'],
           'Diagnosis': ['Diabetes', 'CAD', 'COPD', 'Asthma', 'CHF'],
           'Facility': ['Bapawtist Medical', 'Tampaw General', 'Meowmorial Regional', 'Boca Rawrton Regional', 'Lee Meowmorial'],
           'Language': ['EN', 'EN', 'ES', 'FR', 'EN']}
    data = pd.DataFrame(raw, columns=['Member', 'Diagnosis', 'Facility', 'Language'])

    if request.method == 'POST':
        o = Outreach()
        number = '1{0}'.format(re.sub(r'[^0-9]', '', request.form['number']))
        method = request.form['method']

        randnum = randint(0, 4)
        member = data.iloc[randnum]['Member']
        diagnosis = data.iloc[randnum]['Diagnosis']
        facility = data.iloc[randnum]['Facility']
        language = data.iloc[randnum]['Language']

        if language == 'EN':
            message = 'Hello {0}, we notice that you recently got an authorization for {1} at {2}. Please contact us at (123)456-7890 to see how we can help.'.format(member, diagnosis, facility)
        elif language == 'ES':
            message = 'Hola {0}, we notice that you recently got an authorization for {1} at {2}. Please contact us at (123)456-7890 to see how we can help.'.format(member, diagnosis, facility)
        else:
            message = 'Bonjour {0}, we notice that you recently got an authorization for {1} at {2}. Please contact us at (123)456-7890 to see how we can help.'.format(member, diagnosis, facility)

        if method == 'voice':
            result = PurrtyJSON(o.call(number, message))
        else:
            result = PurrtyJSON(o.text(number, message))

        return render_template('outreach.html', data=data, result=result, title='Outreach Demo')

    return render_template('outreach.html', data=data, result=None, title='Outreach Demo')


#     $$\   $$\ $$$$$$$$\ $$$$$$\ $$\       $$$$$$\ $$$$$$$$\ $$\     $$\
#     $$ |  $$ |\__$$  __|\_$$  _|$$ |      \_$$  _|\__$$  __|\$$\   $$  |
#     $$ |  $$ |   $$ |     $$ |  $$ |        $$ |     $$ |    \$$\ $$  /
#     $$ |  $$ |   $$ |     $$ |  $$ |        $$ |     $$ |     \$$$$  /
#     $$ |  $$ |   $$ |     $$ |  $$ |        $$ |     $$ |      \$$  /
#     $$ |  $$ |   $$ |     $$ |  $$ |        $$ |     $$ |       $$ |
#     \$$$$$$  |   $$ |   $$$$$$\ $$$$$$$$\ $$$$$$\    $$ |       $$ |
#      \______/    \__|   \______|\________|\______|   \__|       \__|
#
#
#
@app.route('/add')
def calculate():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    print a, b
    return jsonify(result=a + b)


@app.route('/download')
@app.route('/download/<filename>')
def download(filename=None):
    # The dictionary below should eventually be a database, so that download counters can be implemented
    files = {}
    files['rsa_members'] = ['rsa_members.csv', 'data', 'RSA Member List']
    files['OMW_auths'] = ['OMW_Fractures_Auths.csv', 'data', 'OMW Auths List']
    files['ROI_workflow'] = ['ROI_Technical_Workflow.docx', 'docs', 'ROI Technical Process Workflow']
    files['ROI_methodology'] = ['ROI_Methodology.docx', 'docs', 'ROI Methodology']
    if filename:
        try:
            # file = open(filepath + '/static/' + files[filename][1] + '/' + files[filename][0], 'r')
            # read = file.read()
            # file.close()
            # response = make_response(read)
            # response.headers['Content-Disposition'] = "attachment; filename=" + files[filename][0]
            # return response
            return send_from_directory(os.path.join(app.config['STATIC_FOLDER'], files[filename][1]), files[filename][0], as_attachment=True)
        except:
            flash('File not found!', 'alert-danger')
            return render_template('download.html', files=files, title='Downloads')

    return render_template('download.html', files=files, title='Downloads')


@app.route('/dbsearch', methods=['GET', 'POST'])
def dbsearch():
    if request.method == 'POST':
        field = request.form['dbField']
        if len(field) < 3:
            flash('Search query must be at least 3 characters!', 'alert-warning')
            return render_template('dbsearch.html', datalist=None, title='Field Search')
        else:
            datalist = pd.read_csv(os.path.join(app.config['STATIC_FOLDER'], 'data', 'db_datalist.csv'))
            datalist = datalist[datalist['Variable Name'].str.contains(field.upper())]
            return render_template('dbsearch.html', datalist=datalist, title='Field Search')

    return render_template('dbsearch.html', datalist=None, title='Field Search')


@app.route('/hedis-extract', methods=['GET', 'POST'])
def hedisExtract():
    # lists for form injection
    measures = pd.read_csv(os.path.join(app.config['STATIC_FOLDER'], 'data', 'hedis_measures.csv'))
    providers = pd.read_csv(os.path.join(app.config['STATIC_FOLDER'], 'data', 'hedis_providers.csv'))

    if request.method == 'POST':
        # fetch form values
        form_measures = request.form.getlist('measure')
        if len(form_measures) == 0:
            form_measures = list(pd.unique(measures[['MEASURE_CODE']].values.ravel()))

        form_providers = request.form.getlist('provider')
        if len(form_providers) == 0:
            form_providers = list(pd.unique(providers[['ATTR_PVDR']].values.ravel()))
            form_providers.append('')

        form_contracts = request.form.getlist('contract')
        if len(form_contracts) == 0:
            form_contracts = ['MED HMO', 'MED RPPO', 'MED LPPO']

        form_pods = re.sub(r'[^0-9]', " ", request.form['pod']).split()
        if len(form_pods) == 0:
            form_pods = [str(x + 1) for x in range(11)]
            form_pods.append('')

        form_zip = re.sub(r'[^0-9]', " ", request.form['zip']).split()
        if len(form_zip) == 0:
            blank_zip = True
        else:
            blank_zip = False

        racf = request.form['racf']

        # generate a hash string for creating a csv file
        hash = '%030x' % randrange(16**30)

        def pullExtract(form_measures, form_providers, form_contracts, form_pods, form_zip, racf, hash, static, uploads):
            import csv
            import os
            from models import email

            # stream extract file
            with open(os.path.join(static, 'data', 'hedis_extract.csv'), 'rb') as extract_in, open(os.path.join(uploads, hash + '.csv'), 'wb') as extract_out:
                in_reader = csv.reader(extract_in)
                out_writer = csv.writer(extract_out)
                header = next(in_reader)
                out_writer.writerow(header)
                for row in in_reader:
                    compliant_indices = []
                    for measure in form_measures:
                        compliant_indices.append(header.index('COMPLIANT_' + measure))
                    if blank_zip:
                        if ('0' in itemgetter(*compliant_indices)(row)) and (row[header.index('ATTR_PVDR')] in form_providers) and (row[header.index('PRODUCT_GROUP')] in form_contracts) and (row[header.index('POD')] in form_pods):
                            out_writer.writerow(row)
                    else:
                        if ('0' in itemgetter(*compliant_indices)(row)) and (row[header.index('ATTR_PVDR')] in form_providers) and (row[header.index('PRODUCT_GROUP')] in form_contracts) and (row[header.index('POD')] in form_pods) and (row[header.index('ZIP_CODE')] in form_zip):
                            out_writer.writerow(row)

            mail_subj = "DELIVERY: Non-Compliant Member HEDIS Extract File " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " SECURE"
            mail_body = "<p>Hello,</p><p>This is an <i>automated</i> message. You recently requested an extract via our <a href='http://wks51b1729:5000/hedis-extract'>HEDIS Extract</a> page. Attached is the generated file.</p><p>Cheers,<br>D3<br><small><a href='http://wks51b1729:5000'>Data Donkey Dashboards</a></small></p>"
            email(racf, mail_subj, mail_body, None, [os.path.join(uploads, hash + '.csv').replace('/', '\\')], True)

        # return send_from_directory(app.config['UPLOAD_FOLDER'], hash + '.csv', as_attachment=True)

        # generate extract pull thread
        pull_thread = threading.Thread(target=pullExtract, args=(form_measures, form_providers, form_contracts, form_pods, form_zip, racf, hash, app.config['STATIC_FOLDER'], app.config['UPLOAD_FOLDER']))
        print "Opening HEDIS Extract thread..."
        pull_thread.start()
        print "Closing thread..."

        flash('A file is being generated for you. An email will send the file as an attachment!', 'alert-success')
        return render_template('hedisextract.html', measures=measures, providers=providers, title='Non-Compliant Member HEDIS Extract')

    return render_template('hedisextract.html', measures=measures, providers=providers, title='Non-Compliant Member HEDIS Extract')


@app.route('/tat', methods=['GET', 'POST'])
def tatReport():
    # lists for form injection
    managers = ['Coler, Art', 'Joseph, Tanisha', 'Robinson, Jacquie', 'Stokes Glover, Johnetta',
                'Williams, Darlene', 'Unknown']
    lobs = ['A65', 'BCG', 'BCI', 'BCR', 'CCG', 'FEP', 'GBO', 'HMO', 'HST', 'IBO', 'IGB', 'MAHMO',
            'MBI', 'MDG', 'MDI', 'MPP', 'MSG', 'MSI', 'POS', 'PPC', 'PPG', 'PPI', 'SAO', 'TRA']
    epclasses = ['Pre Service', 'MA Pre Service', 'Concurrent', 'Post Service', 'FEP Post Service',
                 'FEP', 'FEP Provider PS Appeal', 'VPCR', 'VPCR State', 'MA Post Service']

    if request.method == 'POST':
        # fetch form values
        form_startdt = request.form['startdt']
        form_enddt = request.form['enddt']

        form_managers = request.form.getlist('manager')
        if len(form_managers) == 0:
            form_managers = managers

        form_lobs = request.form.getlist('lob')
        if len(form_lobs) == 0:
            form_lobs = lobs

        form_eptypes = request.form.getlist('eptype')
        if len(form_eptypes) == 0:
            form_eptypes = ['IP', 'OP', 'Appeal']

        form_epclasses = request.form.getlist('epclass')
        if len(form_epclasses) == 0:
            form_epclasses = epclasses

        racf = request.form['racf']

        # generate a hash string for creating output file
        hash = '%030x' % randrange(16**30)

        def pullTat(form_startdt, form_enddt, form_managers, form_lobs, form_eptypes, form_epclasses, racf, hash, static, uploads):
            import itertools
            import os
            import pandas as pd
            from models import email, dbQuery

            # read the SQL file for pulling the data
            file = open(os.path.join(static, 'sql', 'TATReport.sql'), 'r')
            query = file.read()
            file.close()

            # inject paramters into the SQL query
            query_format = (quotify(form_startdt), quotify(form_enddt), ','.join(['?'] * len(form_managers)), ','.join(['?'] * len(form_lobs)), ','.join(['?'] * len(form_eptypes)), ','.join(['?'] * len(form_epclasses)))
            params = list(itertools.chain.from_iterable([form_managers, form_lobs, form_eptypes, form_epclasses]))

            result = dbQuery(query.format(*query_format), 'jiva', params)

            # save to excel
            writer = pd.ExcelWriter(os.path.join(uploads, hash + '.xlsx'), engine='xlsxwriter')
            result.to_excel(writer, sheet_name=form_startdt + ' to ' + form_enddt, index=False)
            writer.save()

            mail_subj = "DELIVERY: UM TAT Report " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " SECURE"
            mail_body = "<p>Hello,</p><p>This is an <i>automated</i> message. You recently requested a run of the <a href='http://wks51b1729:5000/tat'>UM TAT Report</a>. Attached is the generated file.</p><p>Cheers,<br>D3<br><small><a href='http://wks51b1729:5000'>Data Donkey Dashboards</a></small></p>"
            email(racf, mail_subj, mail_body, None, [os.path.join(uploads, hash + '.xlsx').replace('/', '\\')], True)

        # generate asynchronous thread
        pull_thread = threading.Thread(target=pullTat, args=(form_startdt, form_enddt, form_managers, form_lobs, form_eptypes, form_epclasses, racf, hash, app.config['STATIC_FOLDER'], app.config['UPLOAD_FOLDER']))
        print "Opening TAT Report thread..."
        pull_thread.start()
        print "Closing thread..."

        flash('A file is being generated for you. An email will send the file as an attachment!', 'alert-success')
        return render_template('tatreport.html', managers=managers, lobs=lobs, epclasses=epclasses, title='UM TAT Report')

    return render_template('tatreport.html', managers=managers, lobs=lobs, epclasses=epclasses, title='UM TAT Report')


#      $$$$$$\ $$$$$$$$\ $$\   $$\ $$$$$$$$\ $$$$$$$\
#     $$  __$$\\__$$  __|$$ |  $$ |$$  _____|$$  __$$\
#     $$ /  $$ |  $$ |   $$ |  $$ |$$ |      $$ |  $$ |
#     $$ |  $$ |  $$ |   $$$$$$$$ |$$$$$\    $$$$$$$  |
#     $$ |  $$ |  $$ |   $$  __$$ |$$  __|   $$  __$$<
#     $$ |  $$ |  $$ |   $$ |  $$ |$$ |      $$ |  $$ |
#      $$$$$$  |  $$ |   $$ |  $$ |$$$$$$$$\ $$ |  $$ |
#      \______/   \__|   \__|  \__|\________|\__|  \__|
#
#
#
@app.route('/dev')
def jupyter():
    return render_template('jupyter.html', title='Jupyter Notebook')


@app.route('/presentation')
def python():
    return render_template('getpython.html', title='Get Python')


@app.route('/pycourse')
@app.route('/pycourse/<section>')
def pycourse(section=None):
    dirlist = os.listdir(os.path.join(app.config['TEMPLATE_FOLDER'], 'pyintro'))
    chapters = sorted([os.path.splitext(file)[0] for file in dirlist])
    prv = None
    nxt = chapters[1]
    if section:
        if section in chapters:
            secindx = chapters.index(section)
            previndx = secindx - 1
            nextindx = secindx + 1
            if previndx >= 0:
                prv = chapters[previndx]
            else:
                prv = None
            try:
                nxt = chapters[nextindx]
            except IndexError:
                nxt = None
            return render_template('pycourse.html', title='Purrty Python', section='pyintro/' + section + '.html', prv=prv, nxt=nxt, chapters=chapters)
        else:
            flash('Chapter not found!', 'alert-danger')
            return render_template('pycourse.html', title='Purrty Python', section='pyintro/' + chapters[0] + '.html', prv=prv, nxt=nxt, chapters=chapters)

    return render_template('pycourse.html', title='Purrty Python', section='pyintro/' + chapters[0] + '.html', prv=prv, nxt=nxt, chapters=chapters)


#     $$\      $$\  $$$$$$\  $$$$$$\ $$\   $$\
#     $$$\    $$$ |$$  __$$\ \_$$  _|$$$\  $$ |
#     $$$$\  $$$$ |$$ /  $$ |  $$ |  $$$$\ $$ |
#     $$\$$\$$ $$ |$$$$$$$$ |  $$ |  $$ $$\$$ |
#     $$ \$$$  $$ |$$  __$$ |  $$ |  $$ \$$$$ |
#     $$ |\$  /$$ |$$ |  $$ |  $$ |  $$ |\$$$ |
#     $$ | \_/ $$ |$$ |  $$ |$$$$$$\ $$ | \$$ |
#     \__|     \__|\__|  \__|\______|\__|  \__|
#
#
#
if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)

    # app.run(host='0.0.0.0', debug=True)
