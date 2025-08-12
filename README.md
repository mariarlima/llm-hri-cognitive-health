# LLM-Powered Socially Assistive Robots for Cognitive Support

This code is based on the system implementation using for human-robot interaction (HRI) experiments as described in the [paper](https://dl.acm.org/doi/full/10.1145/3706598.3713582) _Promoting Cognitive Health in Elder Care with Large Language Model-Powered Socially Assistive Robots_, presented at [ACM CHI 2025](https://dl.acm.org/doi/proceedings/10.1145/3706598). 

## Abstract
As the global population ages, there is increasing need for accessible technologies that promote cognitive health and detect early signs of cognitive decline.
This study designed an LLM-powered socially assistive robot (SAR) and implemented human-robot verbal dialogue in interactive cognitive tasks based on clinically
validated tools. 
The aim was to evaluate the feasibility of such system to promote cognitive health within residential settings.
We conducted a user study with older adults in retirement homes, involving weekly robot-administered sessions to evaluate cognitive task performance, robot acceptance and verbal engagement. 
This research contributed novel insights into the efficacy of LLM-powered SARs to promote and assess cognitive health in elder care.

## System orchestration
- The system consists of STT, LLM-generated responses, robot behavior, and TTS.
- We designed a multi-agent system that leveraged the linguistic abilities of LLMs for dialogue flexibility and performance in multilingual contexts.
- We integrated a moderator for auto-evaluation as a preventive measure to review LLM-generated responses before they were delivered to participants.
- The length of the robot’s motion sequences were synchronised with its speech duration to promote natural and engaging interactions.

<div align="center">
  <img src="./images/system.png" alt="system" width="400"/>
  <p><em>System implementation of an LLM-powered SAR administering cognitive tasks.</em></p>
</div>


#### Conversational SAR

#### Robot Behaviour

#### Verbal Interaction Design

## Usage
Include your API keys in a `.env` file in the project root directory. 
```
OPENAI_API_KEY=<KEY>
UNREAL_SPEECH_KEY=<KEY>
```

## Citation
If you find this work useful, please consider citing our paper:
```
@inproceedings{lima2025promoting,
  title={Promoting Cognitive Health in Elder Care with Large Language Model-Powered Socially Assistive Robots},
  author={Lima, Maria R and O'Connell, Amy and Zhou, Feiyang and Nagahara, Alethea and Hulyalkar, Avni and Deshpande, Anura and Thomason, Jesse and Vaidyanathan, Ravi and Matari{\'c}, Maja},
  booktitle={Proceedings of the 2025 CHI Conference on Human Factors in Computing Systems},
  pages={1--22},
  year={2025}
}
```
