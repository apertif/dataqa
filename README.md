# dataqa
Scripts for data QA

Wrapper scripts for specific data QA should live at the top level. There are separate directories for scripts/code related to each type of data QA. E.g.

run_crosscalQA.py<br>
crosscal<br>
->ccal_plots.py<br>

## Procedure

1. Log-in to Happili-01

2. Clone the repository to your home

- Example: git clone https://github.com/apertif/dataqa.git

3. Go to the cloned directory (e.g., /home/<user>/dataqa)

4. Run set_up_qa.py 

python set_up_qa.py <obs_id>

- this will create the directory structure by default to /home/<user>/qa_science_demo_2019/<obs_id>

5. Run crosscal qa 

6. Run selfcal qa

7. Run continuum qa

8. Run line qa

9. Run mosaic qa

10. Put relevant information into Google-Doc